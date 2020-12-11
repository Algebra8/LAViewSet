from __future__ import annotations

from typing import (
    NamedTuple,
    Dict,
    Any,
    Callable,
)

import attr
from aiohttp import web


_VIEW = '_view_'
_VIEW_ATTRS = '_view_attrs_'
_exists = object()


def _is_base_path(p: str) -> bool:
    return p == '/'


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

    path: str
    router: web.UrlDispatcher

    name: str = f'Route for {__name__}'  # default name
    is_base: bool = False

    def __add__(self, oroute: Route) -> Route:
        if oroute.router != self.router:
            raise RouteError(
                f'Extensions of {self} must have the same router.'
            )

        return Route(
            self.path + oroute.path,
            self.router,
            name=self.name
        )

    def __attrs_post_init__(self) -> None:
        self.path = self._validate_path(self.path)

    @classmethod
    def create_base(cls, router: web.UrlDispatcher, **kw) -> Route:
        """Creates and returns a base Route.

        The `create_base` method should be preferred for project level
        initialization of the base Route over __init__.
        """
        return Route('', router, is_base=True, **kw)

    def extend(self, path: str) -> Route:
        """Create and return an extension of an existing Route.

        E.g.
            ```
            base_route = Route.create_base(*a, **kw)
            listings_route = base_route.extend('listings')  # /listings/
            ```
        """
        if not path:
            raise RouteError('path must be a valid url path.')

        new_route = Route(path, self.router, self.name)
        return self + new_route

    def __call__(
            self, path: str, method: str,
            **kwargs_for_routedef: Any
    ) -> Callable[..., Any]:
        """Decorator method to wrap a callable (handler), in a "view".
        """
        path = self.path + self._validate_path(path)

        def inner(handler: Callable[..., Any]) -> Callable[..., Any]:
            return _make_view(
                handler,
                ViewAttrs(path, method, kwargs_for_routedef)
            )

        return inner

    def _validate_path(self, path: str) -> str:
        if self.is_base or _is_base_path(path):
            return ''
        if not path.startswith('/'):
            path = f'/{path}'
        return path


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
