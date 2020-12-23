from __future__ import annotations

from typing import cast

import pytest
import mock
from aiohttp import web

from laviewset import routes, rfc
from laviewset.resources import Rfc


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


@pytest.fixture
def strict_route():
    return routes.Route.create_base(
        _fake_router, enforce=rfc.strict)


@pytest.fixture
def non_strict_route():
    return routes.Route.create_base(
        _fake_router, enforce=rfc.non_strict)


@mock.patch('laviewset.routes.ViewAttrs')
def test_enforce_view(mocked_view_attrs, strict_route, view):
    # Our use of rfc.collection is somewhat arbitrary, but also
    # let's us see that the enforcement gets to the view.
    col_resource = strict_route('/listings', 'GET', res_type=rfc.collection)
    _ = col_resource(view)
    mocked_view_attrs.assert_called_once_with(
        '/listings/', 'GET', {}
    )


def test_strict_view_subordinate(strict_route, view):
    sub_resource = strict_route('pk', 'GET', res_type=rfc.subordinate)
    sub_view = sub_resource(view)
    sub_view_attrs = routes.get_view_attrs(sub_view)
    assert sub_view_attrs.path == '/pk'


def test_strict_res_type_fail(strict_route):
    """Test the failing of a strictly enforced view.
    """
    with pytest.raises(routes.RouteError):
        strict_route('/listings', 'GET')  # enforce not set


def test_non_strict_res_type_fail(non_strict_route):
    with pytest.raises(routes.RouteError):
        non_strict_route(
            '/listings', 'GET',
            res_type=rfc.strict     # res_type should not be set with
        )                           # NON-STRICT


def test_enforce_extension(strict_route, non_strict_route):
    # Strict extensions
    s_extended_strict = strict_route.extend('listings', enforce=rfc.strict)
    s_extended_non_strict = strict_route.extend(
        'listings', enforce=rfc.non_strict)

    assert Rfc(s_extended_strict._path.enforce) is Rfc.STRICT
    assert Rfc(s_extended_non_strict._path.enforce) is Rfc.NON_STRICT

    # Non-strict extensions
    ns_s_extended_strict = non_strict_route.extend(
        'listings', enforce=rfc.strict)
    ns_extended_non_strict = non_strict_route.extend(
        'listings', enforce=rfc.non_strict)

    assert Rfc(ns_s_extended_strict._path.enforce) is Rfc.STRICT
    assert Rfc(ns_extended_non_strict._path.enforce) is Rfc.NON_STRICT


def test_enforce_create_base(strict_route, non_strict_route):
    assert Rfc(strict_route._path.enforce) is Rfc.STRICT
    assert Rfc(non_strict_route._path.enforce) is Rfc.NON_STRICT
