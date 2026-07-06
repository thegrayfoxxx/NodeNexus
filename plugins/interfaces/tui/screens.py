from typing import TYPE_CHECKING, cast

from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Static

if TYPE_CHECKING:
    from plugins.interfaces.tui.app import NodeNexusApp


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
    def __init__(self):
        super().__init__()
        self.selected_servers: list[dict] = []
        self.selected_template: dict | None = None

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
            Horizontal(
                Button("Refresh", id="btn-refresh"),
                Button("Clear History", id="btn-clear"),
                Button("Back", id="btn-back"),
            ),
        )

    async def on_mount(self):
        await self.load_history()

    async def on_button_pressed(self, event):
        if event.button.id == "btn-refresh":
            await self.load_history()
        elif event.button.id == "btn-clear":
            await self.clear_history()

    async def load_history(self):
        table = self.query_one(DataTable)
        table.clear()
        app = cast("NodeNexusApp", self.app)
        history = await app.db.get_history()
        for record in history:
            table.add_row(
                str(record.get("executed_at", "")),
                str(record.get("server_name", "")),
                str(record.get("command", "")),
                str(record.get("exit_code", "")),
                f"{record.get('duration', 0):.2f}s",
            )

    async def clear_history(self):
        app = cast("NodeNexusApp", self.app)
        await app.db.clear_history()
        await self.load_history()


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


class TemplateFormScreen(Screen):
    def __init__(self, template: dict | None = None):
        super().__init__()
        self.template = template

    def compose(self):
        title = "Edit Template" if self.template else "Add Template"
        yield Vertical(
            Static(f"=== {title} ===", classes="title"),
            Label("Name:"),
            Input(value=self.template.get("name", "") if self.template else "", id="name"),
            Label("Command:"),
            Input(value=self.template.get("command", "") if self.template else "", id="command"),
            Label("Description:"),
            Input(
                value=self.template.get("description", "") if self.template else "",
                id="description",
            ),
            Horizontal(
                Button("Save", id="btn-save"),
                Button("Cancel", id="btn-cancel"),
            ),
        )
