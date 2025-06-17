import asyncio
import shutil
import os

from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Input

from display_manager import DisplayManager, ActivePopup
from ssh_config_manager import SSHConfigManager
from host_list import HostList

class SSHTUIManagerApp(App):
    CSS_PATH = ["style.tcss"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hosts = SSHConfigManager.load_hosts(Path("~/.ssh/config").expanduser())
        self.host_list = None
        self.active_popup = ActivePopup.NONE
        self.confirmation_future = None

    def compose(self) -> ComposeResult:
        yield from DisplayManager.compose_main_screen(self.hosts)

    async def on_mount(self) -> None:
        self.host_list = self.query_one("#ssh-list", expect_type=HostList)
        self.query_one("#search", Input).focus()

    async def on_input_changed(self, event: Input.Changed)-> None:
        if self.host_list:
            self.host_list.filter_hosts(event.value)

    async def on_key(self, event: events.Key):
        if self.active_popup is not ActivePopup.NONE:
            if event.key == "ctrl+y":
                DisplayManager.close_popup_with_confirmation(self)
            elif event.key in ("ctrl+n", "escape"):
                DisplayManager.close_popup_without_confirmation(self)
            event.stop()
            return

        match event.key:
            case "up":
                if self.host_list:
                    self.host_list.move_selection_up()
                event.stop()
            case "down":
                if self.host_list:
                    self.host_list.move_selection_down()
                event.stop()
            case "enter":
                selected = self.host_list.get_selected_host()
                if selected:
                    await self.launch_ssh(selected)
                event.stop()
            case "ctrl+q" | "ctrl+c" | "escape":
                self.exit()
                event.stop()
            case "ctrl+a":
                asyncio.create_task(self.confirm_and_add())
            case "ctrl+e":
                asyncio.create_task(self.confirm_and_edit(self.host_list.get_selected_host()))
            case "ctrl+d":
                asyncio.create_task(self.confirm_and_delete(self.host_list.get_selected_host()))
                event.stop()

    async def confirm_and_delete(self, selected_host: dict) -> None:
        if not selected_host:
            return

        if await DisplayManager.show_deletion_confirmation_popup(
            self,
            host=selected_host.get("Host", ""),
            user=selected_host.get("User", ""),
            host_name=selected_host.get("HostName", ""),
            port=selected_host.get("Port", ""),
            identity_file=selected_host.get("IdentityFile", "")
        ):
            self.hosts.remove(selected_host)
            self.save_and_update_hosts()

    async def confirm_and_add(self) -> None:
        if await DisplayManager.show_addition_confirmation_popup(self):
            host_input = self.query_one("#host-input", Input)
            user_input = self.query_one("#user-input", Input)
            host_name_input = self.query_one("#host_name-input", Input)
            port_input = self.query_one("#port-input", Input)
            identity_input = self.query_one("#identity-input", Input)

            host = host_input.value.strip()
            user = user_input.value.strip()
            host_name = host_name_input.value.strip()
            port = port_input.value.strip()
            identity = identity_input.value.strip()

            if host:
                new_host = {
                    "Host": host,
                    "User": user,
                    "HostName": host_name,
                    "Port": port,
                    "IdentityFile": identity
                }
                self.hosts.append(new_host)
                self.save_and_update_hosts()

    async def confirm_and_edit(self, selected_host: dict) -> None:
        if not selected_host:
            return

        if await DisplayManager.show_edit_confirmation_popup(
            self,
            host=selected_host.get("Host", ""),
            user=selected_host.get("User", ""),
            host_name=selected_host.get("HostName", ""),
            port=selected_host.get("Port", ""),
            identity_file=selected_host.get("IdentityFile", "")
        ):
            host_input = self.query_one("#host-input", Input)
            user_input = self.query_one("#user-input", Input)
            host_name_input = self.query_one("#host_name-input", Input)
            port_input = self.query_one("#port-input", Input)
            identity_input = self.query_one("#identity-input", Input)

            selected_host["Host"] = host_input.value.strip()
            selected_host["User"] = user_input.value.strip()
            selected_host["HostName"] = host_name_input.value.strip()
            selected_host["Port"] = port_input.value.strip()
            selected_host["IdentityFile"] = identity_input.value.strip()

            self.save_and_update_hosts()


    def save_and_update_hosts(self) -> None:
        SSHConfigManager.save_hosts(Path("~/.ssh/config").expanduser(), self.hosts)
        self.hosts = SSHConfigManager.load_hosts(Path("~/.ssh/config").expanduser())
        self.host_list.refresh_hosts(self.hosts)


    async def launch_ssh(self, host: dict) -> None:
        user = host.get("User", "")
        hostname = host.get("HostName", host.get("Host", ""))
        port = host.get("Port", "")
        identity = host.get("IdentityFile", "")

        if not hostname:
            return

        ssh_connect_command = ["ssh"]
        if user:
            ssh_connect_command += ["-l", user]
        if port:
            ssh_connect_command += ["-p", port]
        if identity:
            ssh_connect_command += ["-i", identity]
        ssh_connect_command.append(hostname)

        terminal_launch_command = self.detect_terminal_launch_command()
        if terminal_launch_command is None:
            self.log("No suitable terminal emulator found")
            return

        asyncio.create_task(self.run_terminal_command(terminal_launch_command + ssh_connect_command))

    def detect_terminal_launch_command(self) -> list[str] | None:
        terminal_environment = os.environ.get("TERMINAL")
        if terminal_environment and shutil.which(terminal_environment):
            return [terminal_environment, "-e"]

        for term, args in [
            ("foot", ["foot", "-e"]),
            ("kitty", ["kitty"]),
            ("wezterm", ["wezterm", "start"]),
            ("alacritty", ["alacritty", "-e"]),
            ("gnome-terminal", ["gnome-terminal", "--"]),
            ("konsole", ["konsole", "-e"]),
            ("xterm", ["xterm", "-e"]),
            ("urxvt", ["urxvt", "-e"]),
        ]:
            if shutil.which(term):
                return args

        return None

    async def run_terminal_command(self, command: list[str]) -> None:
        try:
            process = await asyncio.create_subprocess_exec(*command)
            await process.wait()
        except Exception as e:
            self.log(f"Failed to launch terminal: {e}")
            return
