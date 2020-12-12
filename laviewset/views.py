from __future__ import annotations

from typing import (
    TypeVar,
    Callable,
    Awaitable,
    Any,
    Union,
    List,
    Dict,
    Iterator,
    Tuple,
    cast,
    Mapping,
    NoReturn,
    Generic
)
from ._compat import Protocol
import functools
import inspect
import string
import types

from aiohttp import web

from .routes import (
    Route,
    is_view, get_view_attrs
)
from .mixins import (
    ListMixin,
    RetrieveMixin,
    DestroyMixin,
    UpdateMixin,
    PartialUpdateMixin,
    CreateMixin
)


_T = TypeVar('_T')

_SimpleHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]


class _ViewHandler(Protocol):

    def __call__(
            self, self_: _T,
            web_request: web.Request,
            **kwargs: Any
    ) -> Awaitable[web.StreamResponse]: ...


class _BoundViewHandler(Protocol):

    def __call__(
            self, web_request: web.Request, **kwargs: Any
    ) -> Awaitable[web.StreamResponse]: ...


# _ViewHandler can be considered a subclass of aiohttp.web_routedef
# ._HandlerType, but since it's actually not a subclass, we bundle
# it together with some version of _HandlerType.
_ViewHandlerType = Union[
    _SimpleHandler,
    _ViewHandler,
    _BoundViewHandler
]


def _parse_args(s: str) -> List[str]:
    return [fname for _, fname, _, _ in
            string.Formatter().parse(s) if fname]


def _extract_views(d: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    for name, attr in d.items():
        if is_view(attr):
            yield name, attr


def _create_and_register_routedef(
        handler: _ViewHandlerType,
        router: web.UrlDispatcher
) -> None:
    """Create and register a web.RouteDef.
    """
    attrs = get_view_attrs(handler)

    routedef = web.route(
        attrs.method,
        attrs.path,
        cast(_SimpleHandler, handler),
        **attrs.routedef_kwargs     # kwargs belonging to web.Routedef;
    )                               # not to be mistaken with view's kwargs
    routedef.register(router)


def _check_for_arg_errors(
        params: Mapping[str, inspect.Parameter],
        kw_only: List[str],
        view: _BoundViewHandler
) -> None:
    """
    Validate the signature of a view.

    If an error is raised, it should be of type `ViewSignatureError`.
    """
    # Order matters:
    # KEYWORD_ONLY args should be checked first, otherwise
    # checking for wrong params is catch-all.
    _kw_only_args_error(view, params, kw_only)
    _wrong_params_error(view, kw_only)


def _wrong_params_error(
        view: _BoundViewHandler,
        kw_params: List[str]
) -> None:
    """
    Validate the arg names of the view or raise a `ViewSignatureError`.

    The error occurs if the arg names given in the handler do not
    match the names given to the dynamic resource in @route.

    E.g.

        @route(r'/{pk:\\d+}', HttpMethods.GET)
        async def f(self, request, *, name):  # name != pk
            ...
    """
    view_attrs = get_view_attrs(view)
    parsed_identifiers = _parse_args(view_attrs.path)

    if parsed_identifiers != kw_params:
        view = cast(types.BuiltinFunctionType, view)
        cls_name = view.__self__.__class__.__name__
        func_name = view.__name__
        raise ViewSignatureError(
            f"Bad signature for {cls_name}'s method ``{func_name}``. "
            "Dynamic identifiers must match KEYWORD_ONLY args by both "
            f"variable name and order: {parsed_identifiers} != {kw_params}"
        )


def _kw_only_args_error(
        view: _BoundViewHandler,
        params: Mapping[str, inspect.Parameter],
        kw_params: List[str]
) -> None:
    """
    Validate the arg types of the view.

    If arguments other than `self` and `request` are defined in
    the view signature, then they must be KEYWORD_ONLY.
    Otherwise, raise a `ViewSignatureError`.

    E.g.

        @route(r'/{pk:\\d+}', HttpMethods.GET)
        async def f(self, request, pk):  # should be pk=None or *, pk
            ...
    """
    if len(params) - 1 != len(kw_params):
        # In case the user is unaware of, or forgets, that
        # every argument other than self and request must be
        # KEYWORD_ONLY, we raise an error now instead of letting
        # it break while the server is already running.
        view = cast(types.BuiltinFunctionType, view)
        cls_name = view.__self__.__class__.__name__
        func_name = view.__name__
        raise ViewSignatureError(
            f"Bad signature for {cls_name}'s method ``{func_name}``. "
            "All arguments after `self` and `request` must be "
            "keyword only."
        )


def _get_kwonly_or_raise(view: _BoundViewHandler) -> List[str]:
    """Get KEYWORD_ONLY arguments' name or raise a
    `ViewSignatureError`.
    """
    # Check for arguments other than `self` and `request`.
    # Since other args **must** be KEYWORD_ONLY, it suffices
    # to directly check if any exist.
    params = inspect.signature(view).parameters
    kw_only = [
        name for name, param in params.items()
        if param.kind == param.KEYWORD_ONLY
    ]

    _check_for_arg_errors(params, kw_only, view)

    return kw_only


def _get_handler_from_view(view: _BoundViewHandler) -> _SimpleHandler:
    """
    Wrap and return a handler, as prescribed by aiohttp, over the bound
    view handler defined on the ViewSet.

    Will raise a `ViewSignatureError` for poorly defined view signatures
    during ViewSet build, as opposed to while the app is running.
    """
    # We call _get_kwonly_or_raise here so that we can raise any errors
    # statically, i.e. during class definition build.
    kw_only_args = _get_kwonly_or_raise(view)

    @functools.wraps(view)
    async def handler(request: web.Request) -> web.StreamResponse:
        kwargs = {
            name: request.match_info.get(name)
            for name in kw_only_args
        }

        return await view(request, **kwargs)

    return handler


def raise_404() -> NoReturn:
    raise web.HTTPNotFound()


class ViewSetDefinitionError(ValueError, TypeError):
    """Exception class for ViewSet setup."""


class ViewSignatureError(TypeError):
    """Exception class for view signatures."""


# `empty` allows asserting that the user has
# provided a route attribute to any extended
# ViewSet.
empty = object()

# Since subclassed ViewSets are statically
# constructed, a fake Route api is required to
# construct abstract subclasses of ViewSet.
_fake_app = cast(web.UrlDispatcher, object())
_fake_route = Route('', _fake_app)


class _ViewSet:
    """Class to make sure only `_ViewSet`s use _ViewSetMeta."""

    route = _fake_route


_K = TypeVar('_K', bound=_ViewSet)


class _ViewSetMeta(Generic[_K], type):

    _instances: Dict[_ViewSetMeta[_K], _K] = {}
    route = empty

    def __call__(cls: _ViewSetMeta[_K], *args: Any, **kwargs: Any) -> _K:
        """
        Make any class that uses _ViewSetMeta as a metaclass
        a singleton.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class GenericViewSet(metaclass=_ViewSetMeta):

    route = _fake_route

    def __init_subclass__(cls, **kwargs):
        route = cls.route

        # Make sure a valid route is set on
        # the subclass.
        if route is empty:
            raise ViewSetDefinitionError(
                'Make sure to set route = Route() on ViewSet.'
            )
        if not isinstance(route, Route):
            raise ViewSetDefinitionError(
                '"route" must be of type Route.'
            )
        if route is _fake_route:
            # Avoid ViewSet creation for abstract
            # subclasses of ViewSet.
            return

        for name, attr in _extract_views(cls.__dict__):
            # We have to get the attribute from the class
            # to invoke __getattribute__.
            bound_view = getattr(cls(), name)
            _handler: _SimpleHandler = _get_handler_from_view(bound_view)

            _create_and_register_routedef(
                _handler,
                cls.route.router
            )

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.serializer_class
        return serializer_class(*args, **kwargs)


class ViewSet(GenericViewSet):

    route = _fake_route


class ModelViewSet(
    CreateMixin, RetrieveMixin, UpdateMixin,
    PartialUpdateMixin, DestroyMixin, ListMixin,
    GenericViewSet
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.

    A namesake of, and inspired from, django-rest-framework/ModelViewSet.
    """

    route = _fake_route
    model = None


class ReadOnlyModelViewSet(
    RetrieveMixin, ListMixin,
    GenericViewSet
):
    """
    A viewset that provides default `list()` and `retrieve()` actions.

    A namesake of, and inspired from, django-rest-framework/ReadOnly
    ModelViewSet.
    """

    pass


# Set routes to empty after the construction of any abstract
# subclasses of ViewSet; This is for proper error communication
# in the case that the user does not set a route attribute
# on any concrete subclass of ViewSet.
ViewSet.route = empty
ModelViewSet.route = empty
