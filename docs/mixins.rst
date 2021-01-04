.. module:: laviewset.mixins

.. _mixins-section:

Mixins
--------

Mixins provide the convenience of separating actions into their own structures.
They are used in conjunction with
:class:`GenericViewSet<laviewset.views.GenericViewSet>` to create a ModelViewSet:
a ViewSet that incorporates some or all CRUD actions. In fact,
:class:`ModelViewSet<laviewset.views.ModelViewSet>` and
:class:`ReadOnlyModelViewSet<laviewset.views.ReadOnlyModelViewSet>` are created
with them, as can be seen below.

.. code:: Python



    @make_mixin('/', HttpMethods.GET, 'list')
    class ListMixin:

        async def list(self, request):
            l = await self.model.query.gino.all()
            serializer = self.get_serializer(many=True)
            data = serializer.dump(l)
            return web.json_response(data)


    @make_mixin(r'/{pk:\d+}', HttpMethods.GET, 'retrieve')
    class RetrieveMixin:

        async def retrieve(self, request, *, pk):
            obj = await _get_or_404(self.model, pk)
            serializer = self.get_serializer()
            data = serializer.dump(obj)
            return web.json_response(data)


    class ReadOnlyModelViewSet(
        RetrieveMixin, ListMixin,
        GenericViewSet
    ):
        """
        A viewset that provides default `list()` and `retrieve()`
        actions.

        A namesake of, and inspired from, django-rest-framework/
        ReadOnly ModelViewSet.
        """

        pass


.. _creating-your-own-mixin:

Creating your own mixin
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A custom view mixin can be created by making a class with a single asynchronous
method that would act as the view action, and wrapping the class using the
:py:func:`@make_mixin<make_mixin>` class decorator. A view mixin **must** be used in
conjunction with :class:`GenericViewSet<laviewset.views.GenericViewSet>`.

The code snippet below demostrates the creation of a ViewSet that only has
the ``list`` action: it will only list the data available at the resource
``'/listings'``.

.. code:: Python

    from laviewset import HttpMethods
    from laviewset.mixins import make_mixin
    from laviewset.views import GenericViewSet

    from aiohttp import web

    from ..somewhere import (
        ListingsModel,
        ListingsSchema,
        listings_route
    )

    # ListingsModel:    A Gino model class for Listings
    # ListingsSchema:   A marshmallow Schema for Listings
    # listings_route:   A base_route extension as was demonstrated
    #                   in the routes and views sections.


    @make_mixin('/', HttpMethods.GET, 'list')
    class ListMixin:

        async def list(self, request):
            # ``model`` interface provided by
            # GenericViewSet.
            l = await self.model.query.gino.all()

            # ``get_serializer()`` will return the serializer
            # that exists on GenericViewSet.
            serializer = self.get_serializer(many=True)

            data = serializer.dump(l)
            return web.json_response(data)


    class ListModelViewSet(GenericViewSet, ListMixin):

        route = listings_route  # '/listings'
        model = ListingsModel
        serializer_class = ListingsSchema


The serializer mixin
~~~~~~~~~~~~~~~~~~~~~

As was mentioned in the :ref:`views section<serializer-info>`, the model
ViewSets will expect a serializer class with a specific interface:

    The CRUD mixins that comprise laviewset.ModelViewSet make use
    of an **asynchronous** method on the serializer class that
    it will assume exists on the serializer object: ``is_valid...``.

    The objective of this asynchronous method is to validate
    any deserialized data before using it to modify db objects.

The :class:`SerializerMixin` offers helper methods and an interface to support
the requirements mentioned above.


Mixin interface
~~~~~~~~~~~~~~~~~~~


.. py:function:: make_mixin(path: str, method: str, handler_name: str) -> Callable[Type[T]]

    A class wrapper that will convert the class into a valid mixin that can be
    used with :class:`GenericViewSet<laviewset.views.GenericViewSet>` to create
    variations of :class:`ModelViewSet<laviewset.views.ModelViewSet>`, i.e. actionable
    ViewSets.

    :param path: The path to the mixin's view. E.g. ``'/'`` or ``r'/{pk:\d+}'``.
    :param method: The HTTP method that will activate the mixin's view. E.g. 'GET'.
    :param handler_name: The name of the handler given to the action on the mixin's view.
        For example, ``ListMixin``'s handler is ``async def list(self, request)``, so
        the ``handler_name`` passed into ``make_mixin`` is ``'list'``.

.. raw:: html

    </br>

.. class:: SerializerMixin()

    .. comethod:: is_valid(self, cleaned_data, *args, **kwargs) -> None

        An interface that is used by different mixins to validate any
        deserialized data before modifying db objects.

        :param cleaned_data: Deserialized JSON data in the form of Python objects.

    .. method:: not_valid(self, *, msg: str = '') -> NoReturn

        A convenience method that raises a :ref:`web.HTTPBadRequest<aiohttp-web-exceptions>` with
        ``msg`` as the exception message.
