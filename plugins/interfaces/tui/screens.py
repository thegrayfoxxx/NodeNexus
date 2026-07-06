from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Static


class MainMenuScreen(Screen):
    def compose(self):
        yield Vertical(
            Static("=== NodeNexus Interactive Mode ===", classes="title"),
            Static("Select an option from the sidebar to get started."),
            Static(""),
            Static("Quick Actions:"),
            Static("  • Add a server to get started"),
            Static("  • Create a template for frequent commands"),
            Static("  • Run commands on multiple servers"),
        )


class ServerListScreen(Screen):
    def compose(self):
        table = DataTable()
        table.add_columns("Name", "Host", "Port", "User")
        yield Vertical(
            Static("=== Server Management ===", classes="title"),
            table,
            Horizontal(
                Button("Add Server", id="btn-add"),
                Button("Edit Server", id="btn-edit"),
                Button("Delete Server", id="btn-delete"),
                Button("Back", id="btn-back"),
            ),
        )


class TemplateListScreen(Screen):
    def compose(self):
        table = DataTable()
        table.add_columns("Name", "Command", "Description")
        yield Vertical(
            Static("=== Template Management ===", classes="title"),
            table,
            Horizontal(
                Button("Add Template", id="btn-add"),
                Button("Edit Template", id="btn-edit"),
                Button("Delete Template", id="btn-delete"),
                Button("Back", id="btn-back"),
            ),
        )


class CommandRunnerScreen(Screen):
    def compose(self):
        yield Vertical(
            Static("=== Command Runner ===", classes="title"),
            Label("Select Server:"),
            DataTable(id="server-table"),
            Label("Command (or select template):"),
            Input(placeholder="Enter command...", id="cmd-input"),
            DataTable(id="template-table"),
            Horizontal(
                Button("Run", id="btn-run"),
                Button("Back", id="btn-back"),
            ),
            Static("", id="output-area"),
        )


class HistoryScreen(Screen):
    def compose(self):
        table = DataTable()
        table.add_columns("Time", "Server", "Command", "Exit Code", "Duration")
        yield Vertical(
            Static("=== Command History ===", classes="title"),
            table,
            Button("Back", id="btn-back"),
        )


class ServerFormScreen(Screen):
    def __init__(self, server: dict | None = None):
        super().__init__()
        self.server = server

    def compose(self):
        title = "Edit Server" if self.server else "Add Server"
        yield Vertical(
            Static(f"=== {title} ===", classes="title"),
            Label("Name:"),
            Input(value=self.server.get("name", "") if self.server else "", id="name"),
            Label("Host:"),
            Input(value=self.server.get("host", "") if self.server else "", id="host"),
            Label("Port:"),
            Input(value=str(self.server.get("port", 22)) if self.server else "22", id="port"),
            Label("User:"),
            Input(value=self.server.get("user", "root") if self.server else "root", id="user"),
            Label("Key Path (optional):"),
            Input(value=self.server.get("key_path", "") if self.server else "", id="key_path"),
            Label("Password (optional):"),
            Input(
                value=self.server.get("password", "") if self.server else "",
                password=True,
                id="password",
            ),
            Horizontal(
                Button("Save", id="btn-save"),
                Button("Cancel", id="btn-cancel"),
            ),
        )
