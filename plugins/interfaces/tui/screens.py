from typing import TYPE_CHECKING, cast

from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Label, Static

if TYPE_CHECKING:
    from plugins.interfaces.tui.app import NodeNexusApp


class MainMenuScreen(Vertical):
    def compose(self):
        yield Static("NodeNexus", classes="title")
        yield Static("")
        yield Static("  Добро пожаловать в интерактивный режим!", classes="welcome")
        yield Static("")
        yield Static("  Навигация:", classes="section-title")
        yield Static("    1 - Главное меню")
        yield Static("    2 - Управление серверами")
        yield Static("    3 - Управление шаблонами")
        yield Static("    4 - Выполнение команд")
        yield Static("    5 - Просмотр истории")
        yield Static("    6 - Выход")
        yield Static("")
        yield Static("  Используйте цифры для быстрого доступа", classes="hint")


class ServerListScreen(Vertical):
    BINDINGS = [
        Binding("a", "add", "Добавить"),
        Binding("e", "edit", "Редактировать"),
        Binding("d", "delete", "Удалить"),
        Binding("escape", "back", "Назад"),
    ]

    def compose(self):
        table = DataTable()
        table.add_columns("Имя", "Хост", "Порт", "Пользователь")
        yield Static("Серверы", classes="title")
        yield table
        yield Horizontal(
            Button("[A] Добавить", id="btn-add", variant="primary"),
            Button("[E] Редактировать", id="btn-edit"),
            Button("[D] Удалить", id="btn-delete", variant="error"),
            Button("[Esc] Назад", id="btn-back", variant="default"),
        )

    def action_add(self):
        pass

    def action_edit(self):
        pass

    def action_delete(self):
        pass

    def action_back(self):
        self.app.action_show_main()


class TemplateListScreen(Vertical):
    BINDINGS = [
        Binding("a", "add", "Добавить"),
        Binding("e", "edit", "Редактировать"),
        Binding("d", "delete", "Удалить"),
        Binding("escape", "back", "Назад"),
    ]

    def compose(self):
        table = DataTable()
        table.add_columns("Имя", "Команда", "Описание")
        yield Static("Шаблоны", classes="title")
        yield table
        yield Horizontal(
            Button("[A] Добавить", id="btn-add", variant="primary"),
            Button("[E] Редактировать", id="btn-edit"),
            Button("[D] Удалить", id="btn-delete", variant="error"),
            Button("[Esc] Назад", id="btn-back", variant="default"),
        )

    def action_add(self):
        pass

    def action_edit(self):
        pass

    def action_delete(self):
        pass

    def action_back(self):
        self.app.action_show_main()


class CommandRunnerScreen(Vertical):
    BINDINGS = [
        Binding("enter", "run", "Выполнить"),
        Binding("escape", "back", "Назад"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_servers: list[dict] = []
        self.selected_template: dict | None = None

    def compose(self):
        yield Static("Выполнение команд", classes="title")
        yield Label("Серверы:")
        yield DataTable(id="server-table")
        yield Label("Команда:")
        yield Input(placeholder="Введите команду...", id="cmd-input")
        yield Label("Шаблоны:")
        yield DataTable(id="template-table")
        yield Horizontal(
            Button("[Enter] Выполнить", id="btn-run", variant="success"),
            Button("[Esc] Назад", id="btn-back", variant="default"),
        )
        yield Static("", id="output-area")

    def action_run(self):
        pass

    def action_back(self):
        self.app.action_show_main()


class HistoryScreen(Vertical):
    BINDINGS = [
        Binding("r", "refresh", "Обновить"),
        Binding("x", "clear", "Очистить"),
        Binding("escape", "back", "Назад"),
    ]

    def compose(self):
        table = DataTable()
        table.add_columns("Время", "Сервер", "Команда", "Код", "Длительность")
        yield Static("История команд", classes="title")
        yield table
        yield Horizontal(
            Button("[R] Обновить", id="btn-refresh", variant="primary"),
            Button("[X] Очистить", id="btn-clear", variant="warning"),
            Button("[Esc] Назад", id="btn-back", variant="default"),
        )

    async def on_mount(self):
        await self.load_history()

    async def on_button_pressed(self, event):
        if event.button.id == "btn-refresh":
            await self.load_history()
        elif event.button.id == "btn-clear":
            await self.clear_history()

    def action_refresh(self):
        self.app.run_worker(self.load_history())

    def action_clear(self):
        self.app.run_worker(self.clear_history())

    def action_back(self):
        self.app.action_show_main()

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


class ServerFormScreen(Vertical):
    BINDINGS = [
        Binding("ctrl+s", "save", "Сохранить"),
        Binding("escape", "cancel", "Отмена"),
    ]

    def __init__(self, server: dict | None = None):
        super().__init__()
        self.server = server

    def compose(self):
        title = "Редактирование сервера" if self.server else "Добавление сервера"
        yield Static(title, classes="title")
        yield Label("Имя:")
        yield Input(value=self.server.get("name", "") if self.server else "", id="name")
        yield Label("Хост:")
        yield Input(value=self.server.get("host", "") if self.server else "", id="host")
        yield Label("Порт:")
        yield Input(value=str(self.server.get("port", 22)) if self.server else "22", id="port")
        yield Label("Пользователь:")
        yield Input(value=self.server.get("user", "root") if self.server else "root", id="user")
        yield Label("Путь к ключу:")
        yield Input(value=self.server.get("key_path", "") if self.server else "", id="key_path")
        yield Label("Пароль:")
        yield Input(
            value=self.server.get("password", "") if self.server else "",
            password=True,
            id="password",
        )
        yield Horizontal(
            Button("[Ctrl+S] Сохранить", id="btn-save", variant="success"),
            Button("[Esc] Отмена", id="btn-cancel", variant="default"),
        )

    def action_save(self):
        pass

    def action_cancel(self):
        self.app.action_show_main()


class TemplateFormScreen(Vertical):
    BINDINGS = [
        Binding("ctrl+s", "save", "Сохранить"),
        Binding("escape", "cancel", "Отмена"),
    ]

    def __init__(self, template: dict | None = None):
        super().__init__()
        self.template = template

    def compose(self):
        title = "Редактирование шаблона" if self.template else "Добавление шаблона"
        yield Static(title, classes="title")
        yield Label("Имя:")
        yield Input(value=self.template.get("name", "") if self.template else "", id="name")
        yield Label("Команда:")
        yield Input(value=self.template.get("command", "") if self.template else "", id="command")
        yield Label("Описание:")
        yield Input(
            value=self.template.get("description", "") if self.template else "",
            id="description",
        )
        yield Horizontal(
            Button("[Ctrl+S] Сохранить", id="btn-save", variant="success"),
            Button("[Esc] Отмена", id="btn-cancel", variant="default"),
        )

    def action_save(self):
        pass

    def action_cancel(self):
        self.app.action_show_main()
