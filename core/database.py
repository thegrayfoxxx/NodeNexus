import os

import aiosqlite


class Database:
    def __init__(self, path: str = "~/.nodenexus/nodenexus.db"):
        self.path = path
        self._conn: aiosqlite.Connection

    async def init(self):
        if self.path == ":memory:":
            self._conn = await aiosqlite.connect(self.path)
        else:
            expanded = os.path.expanduser(self.path)
            os.makedirs(os.path.dirname(expanded), exist_ok=True)
            self._conn = await aiosqlite.connect(expanded)
        await self._create_tables()

    async def _create_tables(self):
        await self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER DEFAULT 22,
                user TEXT DEFAULT 'root',
                key_path TEXT,
                password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                command TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                template_id INTEGER,
                command TEXT NOT NULL,
                stdout TEXT,
                stderr TEXT,
                exit_code INTEGER,
                duration REAL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers(id),
                FOREIGN KEY (template_id) REFERENCES templates(id)
            );
        """)
        await self._conn.commit()

    async def add_server(self, name: str, host: str, port: int = 22,
                         user: str = "root", key_path: str | None = None,
                         password: str | None = None) -> int:
        cursor = await self._conn.execute(
            "INSERT INTO servers"
            " (name, host, port, user, key_path, password)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (name, host, port, user, key_path, password),
        )
        await self._conn.commit()
        return cursor.lastrowid or 0

    async def get_servers(self) -> list[dict]:
        cursor = await self._conn.execute("SELECT * FROM servers")
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def update_server(self, server_id: int, **kwargs):
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [server_id]
        await self._conn.execute(
            f"UPDATE servers SET {fields} WHERE id = ?", values
        )
        await self._conn.commit()

    async def delete_server(self, server_id: int):
        await self._conn.execute(
            "DELETE FROM servers WHERE id = ?", (server_id,)
        )
        await self._conn.commit()

    async def add_template(self, name: str, command: str,
                           description: str | None = None) -> int:
        cursor = await self._conn.execute(
            "INSERT INTO templates (name, command, description)"
            " VALUES (?, ?, ?)",
            (name, command, description),
        )
        await self._conn.commit()
        return cursor.lastrowid or 0

    async def get_templates(self) -> list[dict]:
        cursor = await self._conn.execute("SELECT * FROM templates")
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def update_template(self, template_id: int, **kwargs):
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [template_id]
        await self._conn.execute(
            f"UPDATE templates SET {fields} WHERE id = ?", values
        )
        await self._conn.commit()

    async def delete_template(self, template_id: int):
        await self._conn.execute(
            "DELETE FROM templates WHERE id = ?", (template_id,)
        )
        await self._conn.commit()

    async def add_history(self, server_id: int | None, command: str,
                          stdout: str = "", stderr: str = "",
                          exit_code: int = 0, duration: float = 0.0,
                          template_id: int | None = None) -> int:
        cursor = await self._conn.execute(
            "INSERT INTO history"
            " (server_id, template_id, command, stdout, stderr,"
            " exit_code, duration)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (server_id, template_id, command,
             stdout, stderr, exit_code, duration),
        )
        await self._conn.commit()
        return cursor.lastrowid or 0

    async def get_history(self, limit: int = 50) -> list[dict]:
        cursor = await self._conn.execute(
            "SELECT h.*, s.name as server_name"
            " FROM history h"
            " LEFT JOIN servers s ON h.server_id = s.id"
            " ORDER BY h.executed_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def close(self):
        if self._conn:
            await self._conn.close()
