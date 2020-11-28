from __future__ import annotations

from typing import (
    NamedTuple,
    Dict,
    Any,
    Callable,
    Optional
)

import attr
from aiohttp import web

from .resources import Resource


_VIEW = '_view_'
_VIEW_ATTRS = '_view_attrs_'
_exists = object()


def _pop(d: Dict[str, Any], key: str) -> Optional[Any]:
    if key in d:
        val = d.get(key)
        del d[key]
    else:
        val = None
    return val


class ViewAttrs(NamedTuple):

    path: str
    method: str
    routedef_kwargs: Dict[str, Any]  # kwargs to be passed to web.Routedef


def _make_view(
        handler: Callable[..., Any],
        view_attrs: ViewAttrs
) -> Callable[..., Any]:
    """Convert a callable into a view."""
    setattr(handler, _VIEW, _exists)
    setattr(handler, _VIEW_ATTRS, view_attrs)
    return handler


class RouteError(Exception):
    """Exception class for Routes."""


@attr.s(auto_attribs=True)
class Route:

    router: web.UrlDispatcher

    name: Optional[str] = None
    is_base: bool = False
    _path: Optional[Resource] = None

    def __attrs_post_init__(self):
        if self.name is None:
            self.name = f'Route for {__name__}'  # default name

    @property
    def path(self) -> str:
        return str(self._path)

    @path.setter
    def path(self, p: Resource) -> None:
        if not isinstance(p, Resource):
            raise TypeError(f"Can't set path with type {type(p)}")
        self._path = p

    @classmethod
    def create_base(cls, router: web.UrlDispatcher, **kw) -> Route:
        """Creates and returns a base Route.

        The `create_base` method should be preferred for project level
        initialization of the base Route over __init__.
        """
        enforce = _pop(kw, 'enforce')

        route = Route(router, is_base=True, **kw)
        route.path = Resource.create_base(enforce=enforce)
        return route

    def extend(self, path: str, **kw) -> Route:
        """Create and return an extension of an existing Route.

        E.g.
            ```
            base_route = Route.create_base(*a, **kw)
            listings_route = base_route.extend('listings')  # /listings/
            ```
        """
        if not path:
            raise RouteError('path must be a valid url path.')

        new_route = Route(
            self.router,
            name=kw.get('name', f'Extension of {self}')
        )
        new_route.path = self._path.extend(path, enforce=kw.get('enforce'))
        return new_route

    def __call__(
            self, path: str, method: str,
            **kw: Any
    ) -> Callable[..., Any]:
        """Decorator method to wrap a callable (handler), in a "view".
        """
        res_type = _pop(kw, 'res_type')
        try:
            path: Resource = self._path.leaf(path, res_type=res_type)
        except TypeError as te:
            raise RouteError(
                'Incorrect resource type '
                f'for route: {te}'
            ) from None

        # Any kwargs that get through to here
        # will be considered kwargs for web.routedef.
        kwargs_for_routedef = kw

        def inner(handler: Callable[..., Any]) -> Callable[..., Any]:
            return _make_view(
                handler,
                ViewAttrs(str(path), method, kwargs_for_routedef)
            )

        return inner

    def __str__(self):
        return f"Route: {self.name}"


class ViewError(ValueError):
    """Exception class for route wrapped views."""


def is_view(o: Callable[..., Any]) -> bool:
    """Check if a given callable is a "view"."""
    return hasattr(o, _VIEW) and getattr(o, _VIEW) is _exists


def get_view_attrs(o: Callable[..., Any]) -> ViewAttrs:
    """Given a view, get its ViewAttrs.

    If a callable is given and the callable is not a view,
    a `ViewError` will be raised.
    """
    if not is_view(o):
        raise ViewError(
            "Can only get view attributes from a wrapped view, "
            "i.e. if routes.is_view(callable) == True."
        )
    return getattr(o, _VIEW_ATTRS)
