import pytest
import mock
from aiohttp import web

from laviewset import views, routes, HttpMethods


_TEST_RESPONSE = "hello, hows it going?"
_PK = 1
_DATA = {'some': 'data'}


def _generate_var_id_resource(*vals):
    return f'{_TEST_RESPONSE}' + ", ".join(str(val) for val in vals)


@pytest.fixture
def app():
    return web.Application()


@pytest.fixture
def base_route(app):
    return routes.Route.create_base(app.router)


@pytest.fixture
def viewset_core(base_route):

    class TestViewSet(views.ViewSet):

        route = base_route.extend('tests')

        @route('/', HttpMethods.GET)
        async def list(self, request):
            return web.Response(text=_TEST_RESPONSE)

        @route('/', HttpMethods.POST)
        async def create(self, request):
            return web.json_response(_DATA)

        @route(r'/{pk:\d+}', HttpMethods.GET)
        async def retrieve(self, request, *, pk):
            return web.Response(text=_generate_var_id_resource(pk))

        @route(r'/{pk:\d+}', HttpMethods.PUT)
        async def update(self, request, *, pk):
            return web.Response(text=_generate_var_id_resource(pk))

        @route(r'/{pk:\d+}', HttpMethods.PATCH)
        async def partial_update(self, request, *, pk):
            return web.Response(text=_generate_var_id_resource(pk))

        @route(r'/{pk:\d+}', HttpMethods.DELETE)
        async def delete(self, request, *, pk):
            return web.Response(text=_generate_var_id_resource(pk))

    return TestViewSet


@pytest.fixture
def viewset_http_not_found(base_route):
    class TestViewSetFail(views.ViewSet):
        route = base_route.extend('fail')
    return TestViewSetFail


@pytest.fixture
def viewset_custom_methods(base_route):

    class ViewSetWithCustomMethods(views.ViewSet):

        route = base_route.extend('custom')

        @route('/', HttpMethods.GET)
        async def custom_get(self, request):
            return web.Response(text=_TEST_RESPONSE)

        @route('/', HttpMethods.POST)
        async def custom_post(self, request):
            return web.Response(text=_TEST_RESPONSE)

        @route('/', HttpMethods.PUT)
        async def custom_put(self, request):
            return web.Response(text=_TEST_RESPONSE)

        @route('/', HttpMethods.PATCH)
        async def custom_patch(self, request):
            return web.Response(text=_TEST_RESPONSE)

        # Use this view to test multiple dyamic resources.
        @route(r'/{pk:\d+}/{name:\w+}', HttpMethods.DELETE)
        async def custom_delete(self, request, *, pk, name):
            return web.Response(text=_generate_var_id_resource(pk, name))

    return ViewSetWithCustomMethods


@pytest.fixture
def cli_core(loop, aiohttp_client, app, viewset_core):
    """CLI for core view methods defined in laviewset.views.ViewSet."""
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def cli_http_not_found(loop, aiohttp_client, app, viewset_http_not_found):
    """CLI for core view methods that have not been overridden."""
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def cli_custom(loop, aiohttp_client, app, viewset_custom_methods):
    """CLI for core view methods that have not been overridden."""
    return loop.run_until_complete(aiohttp_client(app))


async def test_list(cli_core):
    resp = await cli_core.get('/tests')

    assert resp.status == 200
    assert resp.method == HttpMethods.GET
    assert await resp.text() == _TEST_RESPONSE


async def test_create(cli_core):
    resp = await cli_core.post('/tests')

    assert resp.status == 200
    assert resp.method == HttpMethods.POST
    assert await resp.json() == _DATA


async def test_retrieve(cli_core):
    resp = await cli_core.get(f'/tests/{_PK}')

    assert resp.status == 200
    assert resp.method == HttpMethods.GET
    assert await resp.text() == _generate_var_id_resource(_PK)


async def test_update(cli_core):
    resp = await cli_core.put(f'/tests/{_PK}')

    assert resp.status == 200
    assert resp.method == HttpMethods.PUT
    assert await resp.text() == _generate_var_id_resource(_PK)


async def test_partial_update(cli_core):
    resp = await cli_core.patch(f'/tests/{_PK}')

    assert resp.status == 200
    assert resp.method == HttpMethods.PATCH
    assert await resp.text() == _generate_var_id_resource(_PK)


async def test_delete(cli_core):
    resp = await cli_core.delete(f'/tests/{_PK}')

    assert resp.status == 200
    assert resp.method == HttpMethods.DELETE
    assert await resp.text() == _generate_var_id_resource(_PK)


async def test_http_not_found(cli_http_not_found):
    """
    Test that a method that has not been overridden
    will return a 404.
    """
    resp_list = await cli_http_not_found.get('/fail')
    assert resp_list.status == 404


async def test_multiple_dynamic_resources(cli_custom):
    pk = 123
    name = 'some_name'

    resp = await cli_custom.delete(f'/custom/{pk}/{name}')

    assert resp.status == 200
    assert await resp.text() == _generate_var_id_resource(pk, name)


async def test_custom_get(cli_custom):
    resp = await cli_custom.get('/custom')

    assert resp.status == 200
    assert await resp.text() == _TEST_RESPONSE


async def test_custom_post(cli_custom):
    resp = await cli_custom.post('/custom')

    assert resp.status == 200
    assert await resp.text() == _TEST_RESPONSE


async def test_custom_put(cli_custom):
    resp = await cli_custom.put('/custom')

    assert resp.status == 200
    assert await resp.text() == _TEST_RESPONSE


async def test_custom_patch(cli_custom):
    resp = await cli_custom.patch('/custom')

    assert resp.status == 200
    assert await resp.text() == _TEST_RESPONSE


async def test_custom_delete():
    # This functionality is tested in
    # test_multiple_dynamic_resources
    ...


async def test_wrong_arg_name(base_route):

    with pytest.raises(views.ViewSignatureError):

        class ViewSetFail(views.ViewSet):

            route = base_route.extend('view_fail')

            @route(r'/{pk:\d+}', HttpMethods.GET)
            async def wrong_arg_name(self, request, *, name):
                # This should fail because `name` != `pk`.
                ...


async def test_pos_arg(base_route):
    """Test error raised when POS arg is used in handler signature.

    The error should be raised when one or more POSITIONAL args
    are used in handler signature instead of KEYWORD_ONLY, after
    `self` and `request`.
    """

    with pytest.raises(views.ViewSignatureError):

        class ViewSetFail(views.ViewSet):

            route = base_route.extend('view_fail')

            @route(r'/{pk:\d+}', HttpMethods.GET)
            async def wrong_arg_name(self, request, pk):
                # This should fail because `name` != `pk`.
                ...


async def test_route_not_set(base_route):
    """Test error raised when route object is not set on ViewSet.
    """

    with pytest.raises(views.ViewSetDefinitionError):

        class ViewSetFail(views.ViewSet):

            ...


async def test_wrong_route_type(base_route):
    """Test error raised when route object is not a Route type.
    """

    with pytest.raises(views.ViewSetDefinitionError):

        class ViewSetFail(views.ViewSet):

            route = None

            async def wrong_arg_name(self, request, pk):
                # This should fail because `name` != `pk`.
                ...


# Testing for whether the routedef was correctly created, by
# assuring that `web.route` was called with the expected args,
# along with thorough testing of the client responses should
# represent "the meat" of testing for ViewSet.
@mock.patch('laviewset.views.web.route')
def test_registered_routedef(mock_webroute, base_route):

    class ViewSets(views.ViewSet):

        route = base_route.extend('test')

        @route('/', HttpMethods.GET, z=10)
        async def list(self, request):
            return web.Response(text=_TEST_RESPONSE)

    # We would like to use assert_called_with here, but since a wrapped
    # handler is passed into `laviewset.views._create_and_register_routedef`,
    # which in turn calls `web.route`, we cannot pin the exact object that
    # was passed into the call to web.route as the handler arg from out here
    # (?).
    # As a workaround, we assert it was called once and then make sure all
    # other args, kwargs were called as expected. This method, along with the
    # thorough testing of client responses, should be enough.
    call_args, call_kwargs = mock_webroute.call_args
    mock_webroute.assert_called_once()
    assert call_args[0] == 'GET'
    assert call_args[1] == '/test'
    assert call_kwargs['z'] == 10
