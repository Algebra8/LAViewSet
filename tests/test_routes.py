from __future__ import annotations

from typing import cast

import pytest
from aiohttp import web

from laviewset import routes


_PATH = '/'
_METHOD = 'GET'
_ROUTEDEF_KWARGS = {'z': 123}
_ROUTE_NAME = 'SomeRouter'

_fake_router = cast(web.UrlDispatcher, object())


@pytest.fixture
def view():
    def f(): ...
    setattr(f, '_view_', routes._exists)
    return f


@pytest.fixture
def not_view():
    def f(): ...
    return f


@pytest.fixture
def view_with_attrs(view):
    view_attrs = routes.ViewAttrs(_PATH, _METHOD, _ROUTEDEF_KWARGS)
    setattr(view, '_view_attrs_', view_attrs)
    return view


@pytest.fixture
def base_router():
    return routes.Route.create_base(_fake_router, name=_ROUTE_NAME)


def test_is_view(view, not_view):
    assert routes.is_view(view)
    assert not routes.is_view(not_view)


def test_get_view_attrs(view_with_attrs, not_view):
    view_attrs = routes.get_view_attrs(view_with_attrs)
    assert view_attrs.path == _PATH
    assert view_attrs.method == _METHOD
    assert view_attrs.routedef_kwargs == _ROUTEDEF_KWARGS

    with pytest.raises(routes.ViewError):
        routes.get_view_attrs(not_view)


def test_create_base(base_router):
    assert base_router.is_base
    assert base_router.name == _ROUTE_NAME
    assert base_router.router is _fake_router
    assert base_router.path == ''


def test_extend(base_router):
    r_0 = base_router.extend('/listings')
    assert r_0 != base_router
    assert r_0.path == '/listings'
    # Default name
    assert r_0.name == f'Extension of Route: {base_router.name}'
    assert r_0.router is _fake_router

    r_1 = base_router.extend('listings')
    assert r_1.path == '/listings'


def test_extend_fail(base_router):
    with pytest.raises(routes.RouteError):
        base_router.extend('')


def test_wrapping(base_router):
    test_route = base_router.extend('/tests')
    view_wrapper = test_route(_PATH, _METHOD, **_ROUTEDEF_KWARGS)

    def f(): ...

    view = view_wrapper(f)
    assert routes.is_view(view)

    view_attrs = routes.get_view_attrs(view)
    # Since _PATH is a base path, it should result in '' postfix.
    assert view_attrs.path == test_route.path + ''
    assert view_attrs.method == _METHOD
    assert view_attrs.routedef_kwargs == _ROUTEDEF_KWARGS
