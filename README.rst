LAViewSet
==========

LAViewSet is a ViewSets package, a-la Django Rest Framework - ViewSets, built on top of
`aiohttp <https://github.com/aio-libs/aiohttp>`_, with support for custom ViewSets and
ModelViewSets.



Quick start
------------

To create a custom ViewSet, create a base :class:`~laviewset.routes.Route`,
subclass :class:`~laviewset.views.ViewSet`, and include an
:py:meth:`extension<laviewset.routes.Route.extend>` of the base route on
the ViewSet as the ``route`` attribute:


.. code:: Python

    # laviewset_intro.py

    from aiohttp import web
    from laviewset import Route, ViewSet, HttpMethods

    app = web.Application()
    base_route = Route.create_base(app.router)      # '/'

    class ListingsViewSet(ViewSet):
    """ViewSet for '/listings'"""

        route = base_route.extend('listings')  # '/listings'


The ``route`` on the ViewSet is then :ref:`used as a decorator<route-dec-section>`
to register any asynchronous method into a view handler:

.. code:: Python

    class ListingsViewSet(ViewSet):

        route = base_route.extend('listings')  # '/listings'

        @route('/', HttpMethods.GET)
        async def list(self, request):
            assert isinstance(request, web.Request)
            return web.Response(text="GET at '/listings'")

With the example given above, a ``GET`` request made at ``https://<domain>.com/listings``
will trigger ``ListingsViewSet.list`` and return ``"GET at '/listings'"`` as a
web response.

The ``request`` in ``list``'s signature is in fact an :class:`aiohttp.web.Request`
object, and can be accessed as such.

.. note::

    The handler's :ref:`signature matters<handler-signature-section>`!

For more information on ViewSets, please refer to the :ref:`ViewSets section<viewsets-section>`.


ModelViewSets that offer default actions, similar to Django Rest Framework's ModelViewSet,
can be made using a :class:`~gino.api.Gino` model class and a serializer. While any
serializer class can be used, :class:`marshmallow.Schema<marshmallow.schema.Schema>`
is recommended.

.. code:: Python

    from laviewset import ModelViewSet

    from ..somewhere import (
        ListingsModel,
        ListingsSchema,
        listings_route
    )

    # ListingsModel:    A Gino model class for Listings
    # ListingsSchema:   A marshmallow Schema for Listings
    # listings_route:   '/listings' extension

    class ListingsModelViewSet(ModelViewSet):

        route = listings_route  # '/listings'
        model = ListingsModel
        serializer_class = ListingsSchema


From the code snippet above, the following CRUD operations will be available:

.. list-table::
    :widths: 25 25 50
    :header-rows: 1

    * - Mixin type
      - Http method
      - path
    * - Create
      - POST
      - ``'/listings/'``
    * - List
      - GET
      - ``'/listings/'``
    * - Retrieve
      - GET
      - ``'/listings/{pk:\d+}'``
    * - Destroy
      - DELETE
      - ``'/listings/{pk:\d+}'``
    * - Update
      - PUT
      - ``'/listings/{pk:\d+}'``
    * - PartialUpdate
      - PATCH
      - ``'/listings/{pk:\d+}'``


.. note::

    There are a few interface requirements for the serializer class, so
    please give a brief look at the :ref:`serializer section<serializer-info>`.

For more details on ModelViewSets, please refer
to the :ref:`ModelViewSets section<model-viewset-section>`.



Requirements
------------

* Python >= 3.7
* aiohttp >= 3.6.2
* gino >= 1.0.0
* marshmallow >= 3.0.0


Installing
----------

Install LAViewSet with `pip <https://pip.pypa.io/en/stable/>`_:

.. code:: bash

    pip install laviewset

LICENSE
-------

LAViewSet is offered under the MIT license.

LAViewSet is built on top of `aiohttp <https://github.com/aio-libs/aiohttp>`_
which is distributed under the Apache 2 license.
