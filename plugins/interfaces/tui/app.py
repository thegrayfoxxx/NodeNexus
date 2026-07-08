from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Header, Static

from core.database import Database
from plugins.interfaces.tui.screens import (
    CommandRunnerScreen,
    HistoryScreen,
    MainMenuScreen,
    ServerListScreen,
    TemplateListScreen,
)


class NodeNexusApp(App):
    TITLE = "NodeNexus"
    SUB_TITLE = "Управление удалёнными серверами"
    db: Database

    CSS = """
    Screen {
        layout: vertical;
    }

    #app-container {
        height: 1fr;
    }

    #sidebar {
        width: 32;
        background: $panel;
        border-right: tall $primary;
        padding: 1 0;
    }

    .nav-button {
        width: 100%;
        height: 3;
        margin: 0 1;
        background: $surface;
        border: none;
        color: $text;
        text-align: left;
        padding-left: 2;
    }

    .nav-button:hover {
        background: $primary 30%;
    }

    .nav-button:focus {
        background: $primary 50%;
        color: $text;
    }

    #content {
        width: 1fr;
        padding: 1 2;
    }

    .title {
        text-style: bold;
        color: $primary;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }

    DataTable {
        height: 1fr;
        margin: 1 0;
    }

    Input {
        margin: 0 0 1 0;
    }

    Horizontal {
        height: auto;
        margin: 1 0;
    }

    Button {
        min-width: 16;
        margin: 0 1;
    }

    Label {
        text-style: bold;
        color: $secondary;
        margin-top: 1;
    }

    Static {
        width: 100%;
    }

    #output-area {
        margin-top: 1;
        padding: 1;
        background: $surface;
        border: solid $accent;
        min-height: 5;
    }
    """

    BINDINGS = [
        Binding("1", "show_main", "Главное меню", show=True),
        Binding("2", "show_servers", "Серверы", show=True),
        Binding("3", "show_templates", "Шаблоны", show=True),
        Binding("4", "show_run", "Команда", show=True),
        Binding("5", "show_history", "История", show=True),
        Binding("6", "exit", "Выход", show=True),
        Binding("escape", "show_main", "Меню", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-container"):
            with Vertical(id="sidebar"):
                yield Button("1  Главное меню", id="btn-main", classes="nav-button")
                yield Button("2  Серверы", id="btn-servers", classes="nav-button")
                yield Button("3  Шаблоны", id="btn-templates", classes="nav-button")
                yield Button("4  Команда", id="btn-run", classes="nav-button")
                yield Button("5  История", id="btn-history", classes="nav-button")
                yield Button("6  Выход", id="btn-exit", classes="nav-button")
            with Vertical(id="content"):
                yield Static("Добро пожаловать в NodeNexus!", id="content-area")
        yield Footer()

    async def on_mount(self):
        self.db = Database()
        await self.db.init()
        self._show_screen(MainMenuScreen())

    def _show_screen(self, screen):
        content = self.query_one("#content")
        content.remove_children()
        content.mount(screen)

    def action_show_main(self):
        self._show_screen(MainMenuScreen())

    def action_show_servers(self):
        self._show_screen(ServerListScreen())

    def action_show_templates(self):
        self._show_screen(TemplateListScreen())

    def action_show_run(self):
        self._show_screen(CommandRunnerScreen())

    def action_show_history(self):
        self._show_screen(HistoryScreen())

    def on_button_pressed(self, event):
        if event.button.id == "btn-main":
            self._show_screen(MainMenuScreen())
        elif event.button.id == "btn-servers":
            self._show_screen(ServerListScreen())
        elif event.button.id == "btn-templates":
            self._show_screen(TemplateListScreen())
        elif event.button.id == "btn-run":
            self._show_screen(CommandRunnerScreen())
        elif event.button.id == "btn-history":
            self._show_screen(HistoryScreen())
        elif event.button.id == "btn-exit":
            self.exit()
