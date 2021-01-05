.. module:: laviewset.views

Views
-------------

The idea behind viewsets in laviewset is an asynchronous viewset a-la `Django
Rest Framework - ViewSets <https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset>`_, built on top of
`aiohttp <https://docs.aiohttp.org/en/stable/>`_.
Viewsets  are implemented
by subclassing the :class:`laviewset.ViewSet<laviewset.views.ViewSet>` class.

.. _viewsets-section:

Subclassing and using a ViewSet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to define and use a ViewSet, subclass
:class:`laviewset.ViewSet<laviewset.views.ViewSet>` and include a ``route`` attribute.
The :py:meth:`@route<laviewset.routes.Route.__call__>` decorator can then be used
to wrap any asynchronous method into a valid handler.

.. _viewset-setup:


.. code:: Python

    from aiohttp.web import Application
    from laviewset import Route, ViewSet

    app = Application()
    base_route = Route.create_base(app.router)


    class ListingsViewSet(ViewSet):

        route = base_route.extend('listings')

        @route('/', HttpMethods.GET)
        async def list(self, request):
            return web.Response(text="Get at '/listings'")

.. note::

    Read up on :ref:`the routes section<routes-section>` to learn more about
    routes.

.. _handler-signature-section:

Viewset method signatures and arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The signatures of the views are important. Each view signature requires at
least the ``self`` and ``request`` arguments. The ``request`` is in fact an
:class:`aiohttp.web.Request` object, and can be accessed as such:
:py:attr:`request.query<aiohttp.web.BaseRequest.query>`,
:py:attr:`request.rel_url<aiohttp.web.BaseRequest.rel_url>`, etc,
are all accessible.

.. code:: Python

    class ListingsViewSet(ViewSet):

        route = listings_route

        @route('/', HttpMethods.GET)
        async def list(self, request):
            assert isinstance(request, web.Request)
            return web.Response(text="Get at '/listings'")

If the ``path`` declared in the
:py:meth:`@route <laviewset.routes.Route.__call__>` decorator is a
:ref:`Variable Resource <aiohttp-web-variable-handler>`,
then the *identifier* should be included in the view
signature as a ``KEYWORD_ONLY`` argument **and** have the same name as the
identifier included in the path, otherwise an ``laviewset.ViewSignatureError``
will be raised. This is discussed further in the
:ref:`routes section<path-arg-label>`.

.. code:: Python

    class ListingsViewSet(ViewSet):

        route = listings_route

        @route(r'/{pk:\d+}', HttpMethods.GET)
        async def list(self, request, *, pk):
            ...


Custom views
~~~~~~~~~~~~~~

All :class:`ViewSet<laviewset.views.ViewSet>` handlers
are created equally: there is nothing special about the name
*list*, *retrieve*, *create*, or other common viewset handler names.
Therefore, creating a custom view requires the same steps as those taken to
create the ``list`` view shown above:

.. code:: Python

    class ListingsViewSet(ViewSet):

        route = listings_route

        # Custom GET view
        # '/listings/123/events/Coachella'
        @route(r'/{pk:\d+}/events/{name:\w+}', HttpMethods.GET)
        async def custom_get(self, request, *, pk, name):
            assert pk == 123
            assert name == 'Coachella'
            assert request.method == HttpMethods.GET
            return web.Response(
                text=f'GET at /listings/{pk}/events/{name}'
            )


        # Custom DELETE view
        # '/listings/custom_delete/123/Coachella'
        @route(
            r'/custom_delete/{pk:\d+}/{name:\w+}',
            HttpMethods.DELETE
        )
        async def custom_delete(self, request, *, pk, name):
            assert pk == 123
            assert name == 'Coachella'
            assert request.method == HttpMethods.DELETE
            return web.Response(
                text=f'Deleting {pk} {name}'
            )


.. note::

    The statement "All laviewset.ViewSet handlers
    are created equally" does not apply to
    :class:`ModelViewSets<laviewset.views.ModelViewSet>`.

.. _model-viewset-section:

ModelViewSets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Similar to `Django REST Framework - ModelViewSet <https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset>`_,
:class:`laviewset.ModelViewSet<laviewset.views.ModelViewSet>`
includes implementations for the various CRUD actions, such as DELETE, CREATE, etc.

The ModelViewSet uses :class:`Gino<gino.api.Gino>` for the backend ORM. Check out
`gino-aiohttp <https://pypi.org/project/gino-aiohttp/>`_
for deatils on setting up Gino for your project.


.. note::

    Currently only Gino is supported. Support for other ORMs may be included in
    future versions.


Subclassing and using a ModelViewSet
*************************************

Using an laviewset.ModelViewSet is similar to its *rest_framework.viewsets.ModelViewSet* counterpart:
simply subclass :class:`laviewset.ModelViewSet<laviewset.views.ModelViewSet>`,
include a route (as was done for
:ref:`laviewset.ViewSet<viewset-setup>`), a Gino model class, and a serializer class:

.. code:: Python

    class ListingsModelViewSet(ModelViewSet):

        route = listings_route  # '/listings'
        model = ListingsModel
        serializer_class = ListingsSchema


From the code snippet above, the CRUD operations will be available for
their respective HTTP methods on the path branching from ``listings_route``:

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

    For more information on how to configure and set up a Serializer class,
    refer to the :ref:`serializer section<serializer-info>`.

A more thorough example of using the ModelViewSet, along with serializer
creation and creating a Gino model class, can be seen in the [demos!!!].

.. _serializer-info:

The Serializer class
**********************

A serializer is required for serializing and deserializing objects during
CRUD operations. While any serializer class should theoretically work, laviewset's
ModelViewSet was built with
`marshmallow <https://marshmallow.readthedocs.io/en/stable/>`_ in mind. Therefore,
this documentation will assume the user is using ``marshmallow``.

The CRUD mixins that comprise laviewset.ModelViewSet make use of an
**asynchronous** method on the serializer class that it will assume exists
on the serializer object: ``is_valid(cleaned_data, *args, **kwargs) -> None``.
The objective of this asynchronous method is to validate any deserialized data before using it
to modify db objects.

.. code:: Python

    cleaned_data = serializer.load(data)
    # Validate cleaned data before creating object.
    await serializer.is_valid(cleaned_data)
    _ = await model.create(**cleaned_data)

As a result of this requirement, :class:`SerializerMixin<laviewset.mixins.SerializerMixin>` is
included to be used in conjunction with :class:`marshmallow.schema.Schema`.
This serializer mixin includes the method
:py:meth:`is_valid<laviewset.mixins.SerializerMixin.is_valid>`, which should be overridden,
along with a convenience method,
:py:meth:`not_valid<laviewset.mixins.SerializerMixin.not_valid>`, which raises
a :ref:`web.HTTPBadRequest<aiohttp-web-exceptions>`.

.. code:: Python

    from marshmallow import Schema
    from laviewset import SerializerMixin

    class ListingsSchema(Schema, SerializerMixin):

        async def is_valid(
            self, cleaned_data, *args,
            **kwargs
        ) -> None:
            # Override this method.

            # Could make use of `self.not_valid('some error message')`
            # if validation fails.
            ...

ModelViewSet Flavors
*********************

A :class:`ReadOnlyModelViewSet` is also included with laviewset. This extension of :class:`GenericViewSet`
only provides default ``list()`` and ``retrieve()`` actions. Set up is identical to
ModelViewSet.

.. note::

    To create custom mixins, please refer to the :ref:`mixins<creating-your-own-mixin>` section.

``ViewSet`` interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GenericViewSet()

    An abstract base class that does the heavy lifting behind the scenes: it makes use of
    `__init_subclass__ <https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__>`_
    to register extended class' :py:meth:`@route` wrapped methods with :class:`aiohttp.web.RouteDef`.

.. raw:: html

    </br>

.. class:: ViewSet()

    An asynchronous viewset a-la Django Rest Framework - ViewSets, built on top of aiohttp. It
    is extended from :class:`GenericViewSet`.

    .. py:attribute:: route

        A :class:`Route<laviewset.routes.Route>` object that binds
        :class:`aiohttp.web.UrlDispatcher` to the ViewSet and includes
        the :py:meth:`@route<laviewset.routes.Route.__call__>` decorator.

.. raw:: html

    </br>

.. class:: ModelViewSet()

    An extension of :class:`GenericViewSet` that includes actions for CRUD operations.

    .. py:attribute:: model

        A :class:`Gino<gino.api.Gino>` model class.

    .. py:attribute:: serializer_class

        A serializer class that includes a method with the same signature as
        :py:meth:`is_valid<laviewset.mixins.SerializerMixin.is_valid>`.

        While any class should do, :class:`marshmallow.Schema<marshmallow.schema.Schema>` with :class:`SerializerMixin`
        is recommended.

.. raw:: html

    </br>


.. class:: ReadOnlyModelViewSet()

    A read-only extension of :class:`GenericViewSet` that only includes ``list()`` and
    ``retrieve()`` actions.

    .. py:attribute:: model

        Equivalent to :py:attr:`ModelViewSet.model`.

    .. py:attribute:: serializer_class

        Equivalent to :py:attr:`ModelViewSet.serializer_class`.

