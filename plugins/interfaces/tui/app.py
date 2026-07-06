from textual.app import App, ComposeResult
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
    SUB_TITLE = "Remote Server Management"
    db: Database

    CSS = """
    Screen {
        layout: vertical;
    }
    #sidebar {
        width: 30;
        background: $surface;
        border-right: solid $primary;
    }
    #content {
        width: 1fr;
    }
    .nav-button {
        width: 100%;
        height: 3;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-container"):
            with Vertical(id="sidebar"):
                yield Button("🏠 Main Menu", id="btn-main", classes="nav-button")
                yield Button("🖥️ Servers", id="btn-servers", classes="nav-button")
                yield Button("📋 Templates", id="btn-templates", classes="nav-button")
                yield Button("▶️ Run Command", id="btn-run", classes="nav-button")
                yield Button("📜 History", id="btn-history", classes="nav-button")
                yield Button("❌ Exit", id="btn-exit", classes="nav-button")
            with Vertical(id="content"):
                yield Static("Welcome to NodeNexus!", id="content-area")
        yield Footer()

    async def on_mount(self):
        self.db = Database()
        await self.db.init()
        self.push_screen(MainMenuScreen())

    def on_button_pressed(self, event):
        if event.button.id == "btn-main":
            self.push_screen(MainMenuScreen())
        elif event.button.id == "btn-servers":
            self.push_screen(ServerListScreen())
        elif event.button.id == "btn-templates":
            self.push_screen(TemplateListScreen())
        elif event.button.id == "btn-run":
            self.push_screen(CommandRunnerScreen())
        elif event.button.id == "btn-history":
            self.push_screen(HistoryScreen())
        elif event.button.id == "btn-exit":
            self.exit()
