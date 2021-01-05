LAViewSet
==========

LAViewSet is a ViewSets package, a-la Django Rest Framework - ViewSets, built on top of
`aiohttp <https://github.com/aio-libs/aiohttp>`_, with support for custom ViewSets and
ModelViewSets.


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



ModelViewSets that offer default actions, similar to Django Rest Framework's ModelViewSet,
can be made using a ``Gino`` model class and a serializer. While any
serializer class can be used, ``marshmallow`` is recommended.

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


For more details on ViewSets, ModelViewSets, or other features, such as
building your own ModelViewSet flavor, and a reference to the API, check out
the docs at `https://laviewset.readthedocs.io <https://laviewset.readthedocs.io/en/latest/>`_.


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

LAViewSet is built on top of `aiohttp <https://github.com/aio-libs/aiohttp>`_,
and makes use of `gino <https://github.com/python-gino/gino>`_ and
`marshmallow <https://github.com/marshmallow-code/marshmallow>`_, which are
distributed under the Apache 2 license, BSD License, and MIT License,
respectively.
