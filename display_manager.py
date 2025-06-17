import asyncio
from enum import Enum

from textual.widgets import Input, Static
from textual.containers import Container, Horizontal

from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.containers import Container

from host_list import HostList

class ActivePopup(Enum):
    NONE = 0
    ADD = 1
    EDIT = 2
    DELETE = 3

class DisplayManager:
    def __init__(self):
        self.confirmation_future = None

    @staticmethod
    def compose_main_screen(hosts) -> ComposeResult:
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
            host_list = HostList(hosts, id="ssh-list")
            yield host_list
        with Container(classes="keys-display"):
            yield Horizontal(
                Static("\\[↑/↓]: Navigate", classes="col keys-display-col"),
                Static("\\[Enter]: Connect", classes="col keys-display-col"),
                Static("\\[Ctrl+Q/Ctrl+C/Esc]: Quit", classes="col keys-display-col"),
                Static("\\[Ctrl+A]: Add", classes="col keys-display-col"),
                Static("\\[Ctrl+E]: Edit", classes="col keys-display-col"),
                Static("\\[Ctrl+D]: Delete", classes="col keys-display-col"),
                classes="row"
            )

    @staticmethod
    def hide_normal(app):
        app.query_one("#search", Input).display = False
        app.query(".results-box").first().display = False
        app.query(".keys-display").first().display = False

    @staticmethod
    def show_normal(app):
        app.query_one("#search", Input).display = True
        app.query(".results-box").first().display = True
        app.query(".keys-display").first().display = True

    @staticmethod
    async def show_deletion_confirmation_popup(app, host="", user="", host_name="", port="", identity_file="") -> bool:
        app.active_popup = ActivePopup.DELETE

        DisplayManager.hide_normal(app)
        DisplayManager.construct_deletion_popup(app, host, user, host_name, port, identity_file)

        app.confirmation_future = asyncio.Future()
        result = await app.confirmation_future
        return result

    @staticmethod
    def construct_deletion_popup(app, host="", user="", host_name="", port="", identity_file=""):
        inner_div = Container(
            Container(
                Static("Do you really want to delete this host?"),
                classes="popup-header deletion-popup-header"),
            Container(
                Static(f"Name: {host}\nUser: {user}\nDestination: {host_name}\nPort: {port}\nKey: {identity_file}"),
                classes="popup-body deletion-popup-body"),
            Container(
                Static("\\[Ctrl+Y]: yes", classes="popup-footer-col deletion-popup-footer-col"),
                Static("\\[Ctrl+N/Esc]: no", classes="popup-footer-col"),
                classes="deletion-popup-footer-row"
            ),
            classes="popup deletion-popup"
        )
        popup = Container(
            inner_div,
            id="popup",
            classes="popup-overlay"
        )
        app.mount(popup)

    @classmethod
    def close_popup_with_confirmation(cls, app):
        if app.confirmation_future and not app.confirmation_future.done():
            app.confirmation_future.set_result(True)
        cls._cleanup_popup(app)

    @classmethod
    def close_popup_without_confirmation(cls, app):
        if app.confirmation_future and not app.confirmation_future.done():
            app.confirmation_future.set_result(False)
        cls._cleanup_popup(app)

    @staticmethod
    def _cleanup_popup(app):
        popup = app.query_one("#popup", expect_type=Container)
        popup.remove()
        DisplayManager.show_normal(app)
        app.query_one("#search", Input).focus()
        app.active_popup = ActivePopup.NONE