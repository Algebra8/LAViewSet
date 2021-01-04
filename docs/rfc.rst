
.. module:: laviewset.resources

.. _rfc-section:

RFC strictness
-----------------

laviewset allows the enforcement of "strict" RFC guides for HTTP schemes, as
described in
`this article <https://cdivilly.wordpress.com/2014/03/11/why-trailing-slashes-on-uris-are-important/>`_,
and to some extent in `RFC #3986 <https://tools.ietf.org/html/rfc3986#page-4>`_.
Essentially, strict RFC guides are enforced to the extent that they mean
"enforce trailing slashes".

We attempt to allow the enforcement of trailing slashes through the identifiers
``rfc.strict`` and ``rfc.non_strict``, which are allowed to be inputted in two
API entries: when creating a base route (i.e.
:py:meth:`Route.create_base()<laviewset.routes.Route.create_base>`), and when
extending a route (i.e. :py:meth:`Route.extend()<laviewset.routes.Route.extend>`).

By applying ``rfc.non_strict``, there will be no distinction between a
"collection" resource or a "subordinate" resource. What this means practically
is that URI's will not end in a trailing slash. Consider the following code below:

.. code:: Python

    from aiohttp.web import Application
    from laviewset import Route, ViewSet

    app = Application()
    base_route = Route.create_base(app.router)

    class SomeViewSet(ViewSet):

        route = base_route.extend('/listings')

        @route('/', HttpMethods.GET)
        async def s(self, request): ...

        @route(r'/{pk:int}', HttpMethods.GET)
        async def p(self, request, *, pk): ...



In the above code snippet, the handler ``s`` will only get triggered with a
``GET`` request to the path ``'/listings'``, and ``p`` with a ``GET`` at
``'/listings/{some_integer_id}'``. Note the lack of a trailing slash for both.
Also note how there is no change in how the user will interact with the API
as it was described in any other part of the documentation.

When ``rfc.strict`` is used as an enforcement, some changes do occur. A trailing
slash will be appended to a URI **if** that resource is of type ``rfc.collection``,
which denotes a collection. Otherwise, the resource is a subordinate resource
(and will need to be tagged as such - i.e. ``rfc.subordinate``), which will
result in a URI without a leading slash. Consider the code below:

.. code:: Python

    from aiohttp.web import Application
    from laviewset import Route, ViewSet, rfc

    ...

    class SomeViewSet(ViewSet):

        route = base_route.extend('/listings', enforce=rfc.strict)

        @route('/', HttpMethods.GET, res_type=rfc.collection)
        async def s(self, request): ...

        @route(r'/{pk:int}', HttpMethods.GET, res_type=rfc.subordinate)
        async def p(self, request, *, pk): ...



Now, the handler ``s`` will only be triggered with a ``GET`` at ``'/listings/'``
but ``p`` will be accessible from a ``GET`` at ``'/listings/{some_integer_id}'``.
Note the trailing slash for ``s`` but none for ``p``.

It is important to note a few more things:

* If ``strict`` is used, a ``res_type`` **must** be provided by the user in the :py:meth:`@route<laviewset.routes.Route.__call__>` decorator. Otherwise a :class:`RouteError<laviewset.routes.RouteError>` will be raised from a ``TypeError``.

* If ``non_strict`` is used, ``res_type`` should not be provided - a ``RouteError`` will be raised otherwise.

* At anytime during the API entries (i.e. ``Route.create_base()``, ``Route.extend()``), the enforcement policy can be overridden.

* If the enforcement policy is not overridden for an extension (i.e. ``Route.extend()``), then the parent ``Resource``'s enforcement will be used.

* The default value for the API entries is ``rfc.non_strict``.
