from textual.widgets import ListView, ListItem, Static
from textual.containers import Horizontal
from textual import events
from rich.text import Text



class SSHList(ListView):
    def __init__(self, hosts: list[dict], **kwargs):
        super().__init__(**kwargs)
        self.hosts = hosts
        self.filtered = hosts.copy()
        self.current_query = ""
        self.selected_index = 0

    async def on_mount(self):
        self.refresh_list()

    def refresh_list(self):
        self.clear()
        if not self.filtered:
            self.mount(ListItem(Static("")))
            self.selected_index = 0
        else:
            for idx, host in enumerate(self.filtered):
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
                if idx == self.selected_index:
                    item.add_class("selected")
                self.mount(item)


    def filter(self, query: str):
        self.current_query = query.lower()
        self.filtered = [h for h in self.hosts if self.current_query in h["Host"].lower()]
        self.selected_index = 0
        self.refresh_list()

    def highlight_match(self, text: str, query: str) -> Text:
        if not query:
            return Text(text)

        highlighted = Text()
        start = 0

        while True:
            idx = text.lower().find(query.lower(), start)
            if idx == -1:
                highlighted.append(text[start:])
                break
            highlighted.append(text[start:idx])
            highlighted.append(text[idx:idx+len(query)], style="#a6e3a1")
            start = idx + len(query)
        return highlighted

    def move_selection_up(self):
        if not self.filtered:
            return
        self.selected_index = (self.selected_index - 1) % len(self.filtered)
        self.refresh_list()
        self.scroll_to_selected()

    def move_selection_down(self):
        if not self.filtered:
            return
        self.selected_index = (self.selected_index + 1) % len(self.filtered)
        self.refresh_list()
        self.scroll_to_selected()

    def scroll_to_selected(self):
        if self.children:
            selected_item = self.children[self.selected_index]
            self.scroll_to(selected_item)

    def get_selected_host(self) -> dict | None:
        if not self.filtered:
            return None
        return self.filtered[self.selected_index]
