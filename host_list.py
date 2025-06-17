from textual.widgets import ListView, ListItem, Static
from textual.containers import Horizontal
from textual import events
from rich.text import Text



class HostList(ListView):
    def __init__(self, all_hosts: list[dict], **kwargs):
        super().__init__(**kwargs)
        self.all_hosts = all_hosts
        self.filtered_hosts = all_hosts.copy()
        self.current_query = ""
        self.index_selected_host = 0

    def refresh_hosts(self, new_hosts: list[dict]) -> None:
        self.all_hosts = new_hosts
        self.filtered_hosts = new_hosts.copy()
        self.current_query = ""
        self.index_selected_host = 0
        self.refresh_list()

    async def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        self.clear()
        if not self.filtered_hosts:
            self.mount(ListItem(Static("...")))
            self.index_selected_host = 0
        else:
            for index_current_host, host in enumerate(self.filtered_hosts):
                host_text = self.highlight_match(host.get("Host", ""), self.current_query)
                row = Horizontal(
                    Static(host_text, classes="col"),
                    Static(host.get("User", ""), classes="col"),
                    Static(host.get("HostName", ""), classes="col"),
                    Static(host.get("Port", ""), classes="col"),
                    Static(host.get("IdentityFile", ""), classes="col"),
                    classes="row"
                )
                item = ListItem(row)
                if index_current_host == self.index_selected_host:
                    item.add_class("selected-row")
                self.mount(item)


    def filter_hosts(self, query: str) -> None:
        self.current_query = query.lower()
        self.filtered_hosts = [h for h in self.all_hosts if self.current_query in h["Host"].lower()]
        self.index_selected_host = 0
        self.refresh_list()

    def highlight_match(self, text: str, query: str) -> Text:
        if not query:
            return Text(text)

        highlighted = Text()
        start = 0

        while True:
            index_match = text.lower().find(query.lower(), start)
            if index_match == -1:
                highlighted.append(text[start:])
                break
            highlighted.append(text[start:index_match])
            highlighted.append(text[index_match:index_match+len(query)], style="#4bcb3c")
            start = index_match + len(query)
        return highlighted

    def move_selection_up(self) -> None:
        if not self.filtered_hosts:
            return
        self.index_selected_host = (self.index_selected_host - 1) % len(self.filtered_hosts)
        self.refresh_list()
        self.highlight_selected()

    def move_selection_down(self) -> None:
        if not self.filtered_hosts:
            return
        self.index_selected_host = (self.index_selected_host + 1) % len(self.filtered_hosts)
        self.refresh_list()
        self.highlight_selected()

    def highlight_selected(self) -> None:
        if self.children and 0 <= self.index_selected_host < len(self.children):
            selected_item = self.children[self.index_selected_host]
            self.scroll_to(selected_item)

    def get_selected_host(self) -> dict | None:
        if not self.filtered_hosts:
            return None
        return self.filtered_hosts[self.index_selected_host]
