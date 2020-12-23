import pytest
from aiohttp import web

from laviewset import Route
from .models import User, PG_URL, db

pytestmark = pytest.mark.asyncio


async def db_startup(_):
    await db.set_bind(PG_URL)
    await db.gino.create_all()

    await User.create(id=1, nickname='test1')
    await User.create(id=2, nickname='test2')
    await User.create(id=3, nickname='test3')


async def db_shutdown(_):
    await db.gino.drop_all()
    await db.pop_bind().close()


@pytest.fixture
async def get_all_users():
    return await User.query.gino.all()


@pytest.fixture
async def get_user_1(get_all_users):
    return get_all_users[0]


@pytest.fixture
def db_app():
    app = web.Application()
    app.on_startup.append(db_startup)
    app.on_shutdown.append(db_shutdown)
    return app


@pytest.fixture
def db_router(db_app):
    base_route = Route.create_base(db_app.router)
    return base_route
