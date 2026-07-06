from typing import TYPE_CHECKING, cast

from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Static

if TYPE_CHECKING:
    from plugins.interfaces.tui.app import NodeNexusApp


class MainMenuScreen(Screen):
    def compose(self):
        yield Vertical(
            Static("=== NodeNexus — Интерактивный режим ===", classes="title"),
            Static("Выберите опцию в боковом меню для начала работы."),
            Static(""),
            Static("Быстрые действия:"),
            Static("  • Добавьте сервер для начала работы"),
            Static("  • Создайте шаблон для частых команд"),
            Static("  • Выполняйте команды на нескольких серверах"),
        )


class ServerListScreen(Screen):
    def compose(self):
        table = DataTable()
        table.add_columns("Имя", "Хост", "Порт", "Пользователь")
        yield Vertical(
            Static("=== Управление серверами ===", classes="title"),
            table,
            Horizontal(
                Button("Добавить", id="btn-add"),
                Button("Редактировать", id="btn-edit"),
                Button("Удалить", id="btn-delete"),
                Button("Назад", id="btn-back"),
            ),
        )


class TemplateListScreen(Screen):
    def compose(self):
        table = DataTable()
        table.add_columns("Имя", "Команда", "Описание")
        yield Vertical(
            Static("=== Управление шаблонами ===", classes="title"),
            table,
            Horizontal(
                Button("Добавить", id="btn-add"),
                Button("Редактировать", id="btn-edit"),
                Button("Удалить", id="btn-delete"),
                Button("Назад", id="btn-back"),
            ),
        )


class CommandRunnerScreen(Screen):
    def __init__(self):
        super().__init__()
        self.selected_servers: list[dict] = []
        self.selected_template: dict | None = None

    def compose(self):
        yield Vertical(
            Static("=== Выполнение команд ===", classes="title"),
            Label("Выберите сервер:"),
            DataTable(id="server-table"),
            Label("Команда (или выберите шаблон):"),
            Input(placeholder="Введите команду...", id="cmd-input"),
            DataTable(id="template-table"),
            Horizontal(
                Button("Выполнить", id="btn-run"),
                Button("Назад", id="btn-back"),
            ),
            Static("", id="output-area"),
        )


class HistoryScreen(Screen):
    def compose(self):
        table = DataTable()
        table.add_columns("Время", "Сервер", "Команда", "Код выхода", "Длительность")
        yield Vertical(
            Static("=== История команд ===", classes="title"),
            table,
            Horizontal(
                Button("Обновить", id="btn-refresh"),
                Button("Очистить историю", id="btn-clear"),
                Button("Назад", id="btn-back"),
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
        title = "Редактирование сервера" if self.server else "Добавление сервера"
        yield Vertical(
            Static(f"=== {title} ===", classes="title"),
            Label("Имя:"),
            Input(value=self.server.get("name", "") if self.server else "", id="name"),
            Label("Хост:"),
            Input(value=self.server.get("host", "") if self.server else "", id="host"),
            Label("Порт:"),
            Input(value=str(self.server.get("port", 22)) if self.server else "22", id="port"),
            Label("Пользователь:"),
            Input(value=self.server.get("user", "root") if self.server else "root", id="user"),
            Label("Путь к ключу (необязательно):"),
            Input(value=self.server.get("key_path", "") if self.server else "", id="key_path"),
            Label("Пароль (необязательно):"),
            Input(
                value=self.server.get("password", "") if self.server else "",
                password=True,
                id="password",
            ),
            Horizontal(
                Button("Сохранить", id="btn-save"),
                Button("Отмена", id="btn-cancel"),
            ),
        )


class TemplateFormScreen(Screen):
    def __init__(self, template: dict | None = None):
        super().__init__()
        self.template = template

    def compose(self):
        title = "Редактирование шаблона" if self.template else "Добавление шаблона"
        yield Vertical(
            Static(f"=== {title} ===", classes="title"),
            Label("Имя:"),
            Input(value=self.template.get("name", "") if self.template else "", id="name"),
            Label("Команда:"),
            Input(value=self.template.get("command", "") if self.template else "", id="command"),
            Label("Описание:"),
            Input(
                value=self.template.get("description", "") if self.template else "",
                id="description",
            ),
            Horizontal(
                Button("Сохранить", id="btn-save"),
                Button("Отмена", id="btn-cancel"),
            ),
        )
