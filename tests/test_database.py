from core.database import Database

import pytest


@pytest.fixture
async def db():
    database = Database(":memory:")
    await database.init()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_add_server(db):
    server_id = await db.add_server(
        name="test-server",
        host="example.com",
        port=22,
        user="admin",
    )
    assert server_id is not None
    servers = await db.get_servers()
    assert len(servers) == 1
    assert servers[0]["name"] == "test-server"


@pytest.mark.asyncio
async def test_add_template(db):
    template_id = await db.add_template(
        name="uptime",
        command="uptime",
        description="Show server uptime",
    )
    assert template_id is not None
    templates = await db.get_templates()
    assert len(templates) == 1
    assert templates[0]["name"] == "uptime"


@pytest.mark.asyncio
async def test_add_history(db):
    server_id = await db.add_server(
        name="test-server",
        host="example.com",
        port=22,
        user="admin",
    )
    history_id = await db.add_history(
        server_id=server_id,
        command="ls",
        stdout="file.txt",
        stderr="",
        exit_code=0,
        duration=0.5,
    )
    assert history_id is not None
    history = await db.get_history()
    assert len(history) == 1
