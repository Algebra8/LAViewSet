.. module:: laviewset.routes
.. _routes-section:

Routes
-------------

The :class:`Route <laviewset.routes.Route>` object is the conduit between
an :class:`aiohttp.web.UrlDispatcher`
and any :class:`ViewSet <laviewset.views.ViewSet>`.


Route creation begins with the
:py:meth:`create_base() <laviewset.routes.Route.create_base>`
method, which requires a UrlDispatcher. This "base route" can then be extended
to specific URL branches with the
:py:meth:`extend() <laviewset.routes.Route.extend>` method.

.. code:: Python

    from aiohttp import web
    from laviewset import Route

    app = web.Application()
    base_route = Route.create_base(app.router)

    print(base_route.path)      # ''

    listings_route = base_route.extend('listings')
    sessions_route = base_route.extend('sessions')

    print(listings_route.path)  # '/listings'
    print(sessions_route.path)  # '/sessions'

A branch can then be used as a class attribute on a ViewSet, linking
that branch's url path to the handles defined on the ViewSet with the
:py:meth:`@route <laviewset.routes.Route.__call__>`
decorator.

.. _base_and_view:

.. code:: Python

    from aiohttp import web
    from laviewset import Route, ViewSet, HttpMethods

    # Get `listings_route` as described above.
    ...

    class ListingsViewSet(ViewSet):

        route = listings_route

        @route('/', HttpMethods.GET)
        async def list(self, request):
            assert isinstance(request, web.Request)
            return web.Response(text="Get at '/listings'")


With the code snippet above, a **GET** request to *https://<domain>.com/listings*
will return ``"Get at '/listings'"`` as a web response.

The ``@route`` decorator: defining views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :py:meth:`@route <laviewset.routes.Route.__call__>` decorator wraps a handler
in a *view*. A view is essentially a wrapper over
:func:`aiohttp.web.route`; the arguments passed into the decorator correspond
with the arguments for :func:`web.route<>`: the first argument is the path, the second
is the HTTP method, and any other keyword arguments passed into the
decorator will be included as ``kwargs`` to :func:`web.route<>`.

.. note::

    The view itself will be passed to :func:`web.route<>`
    as the ``handler``.


The ``@route`` decorator: ``path``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``path``, the first argument to **@route**, deserves further analysis.
Any argument passed to it will be appended to the **Route.path** attribute
of the :class:`Route<>` object attached to the :class:`ViewSet`.

.. code:: Python

    class ListingsViewSet(ViewSet):

        route = listings_route

        @route('/abc', HttpMethods.GET)
        async def some_handler(self, request):
            # GET at /listings/abc

            # The path 'abc' is appended to the
            # path '/listings' of `listings_route`.
            ...


The argument is optional and will default to ``'/'``, although it is recommended
for readability to include it instead of falling to the default value.

A forward slash will denote an HTTP request to the path of the route,
:ref:`as can be seen in this code snippet<base_and_view>`. Any valid path can
be provided, even multiple paths: ``'/abc/def'`` in the example above
will result in ``'listings/abc/def'`` as the path.

.. _path-arg-label:

The path can also be a :ref:`Variable Resource <aiohttp-web-variable-handler>`.
In this case the
*identifier* portion should be included in the view's signature as a ``KEYWORD_ONLY``
argument **and** have the same name as the identifier:

.. code:: Python

    class SessionsViewSet(ViewSet):

        route = sessions_route

        # Correct
        # GET at sessions/{pk}
        @route(r'/{pk:\d+}', HttpMethods.GET)
        async def first_handler(self, request, *, pk):
            # `pk` is KEYWORD_ONLY
            # `pk` is same as identifier
            ...

        # Incorrect
        @route(r'/{pk:\d+}', HttpMethods.GET)
        async def second_handler(self, request, pk):
            # `pk` is not KEYWORD_ONLY
            ...

        # Incorrect
        @route(r'/{pk:\d+}', HttpMethods.GET)
        async def third_handler(self, request, *, fk):
            # `pk` != `fk`
            ...

.. note::

    Incorrect signatures will result in a
    :class:`ViewSignatureError<laviewset.ViewSignatureError>`.


``Route`` interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: Route()

    Conduit between :class:`aiohttp.web.UrlDispatcher` and
    :class:`~laviewset.views.GenericViewSet`.

    Provides functionality for creating a web handler on
    the ViewSet and managing URLs.

    .. raw:: html

        </br

    .. classmethod:: create_base(router: web.UrlDispatcher) -> Route

        Route factory for creating a base route.

        :param router: An :class:`aiohttp.web.UrlDispatcher` which will be used
         to register the handlers.

    .. raw:: html

        </br>

    .. method:: extend(path: str, **kwargs: Any) -> Route

        Create and return an extension of an existing Route.

        The path of the new Route object will be determined by
        the ``path`` argument.

    .. raw:: html

        </br>

    .. method:: __call__(path: str, method: str, **kwargs: Any) -> Callable[..., Any]

        Decorator to wrap a callable (handler), in a "view".

        This decorator is used on a ViewSet (or any valid subclass of
        :class:`~laviewset.views.GenericViewSet`), to convert an asynchronous
        method into a handler.

        :param path: The extension of the ``self.path`` that will be used
         to activate an endpoint. For example, if ``Route.path`` is ``'/listings'``
         and ``path='abc'``, then the wrapped handler will be activated by the
         resource ``'/listings/abc'``.

        :param method: The HTTP method that activates the endpoint.

        :param res_type: An optional KEYWORD_ONLY argument that signifies
         whether the resource is a collection or subordinate. It is only relevant
         when using ``rfc.strict``. See :ref:`RFC strictness<rfc-section>` for
         more information.

        :param kwargs: Any keyword arguments passed into the function, other than
         those that are directly related to the Route, will be passed on as arguments
         to the underlying :class:`aiohttp.web.Routedef` object.
