import json

import pytest

from laviewset import ModelViewSet
from .models import User, UserSchema

_serializer_class = UserSchema


@pytest.fixture
def model_viewset_core(db_router):

    class SomeViewSet(ModelViewSet):

        route = db_router.extend('users')
        model = User
        serializer_class = UserSchema

    return SomeViewSet


@pytest.fixture
def db_cli_core(loop, aiohttp_client, db_app, model_viewset_core):
    return loop.run_until_complete(aiohttp_client(db_app))


async def test_list(db_cli_core, get_all_users):
    resp = await db_cli_core.get('/users')
    assert resp.status == 200

    dat = await resp.json()
    assert dat == _serializer_class(many=True).dump(get_all_users)


async def test_retrieve(db_cli_core, get_user_1):
    resp = await db_cli_core.get('/users/1')
    assert resp.status == 200

    dat = await resp.json()
    assert dat == _serializer_class().dump(get_user_1)


async def test_create(db_cli_core):
    data = {'id': 4, 'nickname': 'new_user'}
    resp = await db_cli_core.post('/users', data=json.dumps(data))
    assert resp.status == 201

    dat = await resp.json()
    assert dat['id'] == data['id']
    assert dat['nickname'] == 'new_user'

    assert resp.headers['Location'] == f"{resp.url}/{data['id']}"


async def test_delete(db_cli_core):
    resp = await db_cli_core.delete('/users/1')
    assert resp.status == 204

    attempt_get = await db_cli_core.get('/users/1')
    assert attempt_get.status == 404


async def test_partial_update(db_cli_core):
    data = {'nickname': 'patched_nickname'}
    resp = await db_cli_core.patch('/users/1', data=json.dumps(data))
    assert resp.status == 200

    patched_attempt = await db_cli_core.get('/users/1')
    patched = await patched_attempt.json()
    assert patched['nickname'] == data['nickname']


async def test_update(db_cli_core):
    partial_data = {'nickname': 'patched_nickname'}
    bad_request_resp = await db_cli_core.put(
        '/users/1',
        data=json.dumps(partial_data)
    )
    assert bad_request_resp.status == 400

    full_data = {'id': 1, 'nickname': 'patched_nickname'}
    ok_resp = await db_cli_core.put(
        '/users/1',
        data=json.dumps(full_data)
    )
    assert ok_resp.status == 200

    put_attempt = await db_cli_core.get('/users/1')
    put = await put_attempt.json()
    assert put['id'] == full_data['id']
    assert put['nickname'] == full_data['nickname']
