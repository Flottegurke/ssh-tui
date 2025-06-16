from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from textual.containers import Container, Horizontal
from textual.events import Key

from ssh_config_loader import SSHConfigLoader
from ssh_list import SSHList

import asyncio
import shutil
import os

class SSHManagerApp(App):
    CSS_PATH = ["style.tcss"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hosts = SSHConfigLoader.load_hosts(Path("~/.ssh/config").expanduser())
        self.ssh_list = None

    def compose(self) -> ComposeResult:
        yield Input(id="search")
        with Container(classes="results-box"):
            yield Horizontal(
                Static("Name:", classes="col"),
                Static("User:", classes="col"),
                Static("Destination:", classes="col"),
                Static("Port:", classes="col"),
                Static("Key:", classes="col"),
                classes="header-row row"
            )
            self.ssh_list = SSHList(self.hosts, id="ssh-list")
            yield self.ssh_list
        with Container(classes="keys-display"):
            yield Horizontal(
                Static("\\[↑/↓]: Navigate", classes="col keys-display-col"),
                Static("\\[Enter]: Connect", classes="col keys-display-col"),
                Static("\\[Ctrl+Q/Ctrl+C/Esc]: Quit", classes="col keys-display-col"),
                classes="row"
            )

    async def on_mount(self):
        self.query_one("#search", Input).focus()

    async def on_input_changed(self, event: Input.Changed):
        if self.ssh_list:
            self.ssh_list.filter(event.value)

    async def on_key(self, event: Key) -> None:
        match (event.key):
            case ("up"):
                if self.ssh_list:
                    self.ssh_list.move_selection_up()
                event.stop()
            case ("down"):
                if self.ssh_list:
                    self.ssh_list.move_selection_down()
                event.stop()
            case ("enter"):
                selected = self.ssh_list.get_selected_host()
                if selected:
                    await self.launch_ssh(selected)
                event.stop()
            case ("ctrl+q") | ("ctrl+c") | ("escape"):
                self.exit()
                event.stop()

    async def launch_ssh(self, host: dict):
        user = host.get("User", "")
        hostname = host.get("HostName", host.get("Host", ""))
        port = host.get("Port", "")
        identity = host.get("IdentityFile", "")

        if not hostname:
            return

        cmd = ["ssh"]
        if user:
            cmd += ["-l", user]
        if port:
            cmd += ["-p", port]
        if identity:
            cmd += ["-i", identity]
        cmd.append(hostname)

        terminal_cmd = self.detect_terminal_command()
        if terminal_cmd is None:
            self.log("No suitable terminal emulator found")
            return

        asyncio.create_task(self.run_terminal_command(terminal_cmd + cmd))


    async def run_terminal_command(self, command: list[str]):
        try:
            pid = await asyncio.create_subprocess_exec(*command)
        except Exception as e:
            self.log(f"Failed to launch terminal: {e}")
            return

    def detect_terminal_command(self):
        env_term = os.environ.get("TERMINAL")
        if env_term and shutil.which(env_term):
            return [env_term, "-e"]

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