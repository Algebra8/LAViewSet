from aiohttp import web
from .http_meths import HttpMethods


# Need to override __init_subclass__ for each action mixin.
# A call to super() is necessary so that the next action mixin
# in a subclassed ViewSet has __init_subclass__ called as well.
class ListMixin:

    def __init_subclass__(cls, **kwargs):
        wrapper = cls.route('/', HttpMethods.GET)
        setattr(cls, 'list', wrapper(cls.list))

        super().__init_subclass__()

    async def list(self, request):
        return web.Response(text='at list!')


class RetrieveMixin:

    def __init_subclass__(cls, **kwargs):
        wrapper = cls.route(r'/{pk:\d+}', HttpMethods.GET)
        setattr(cls, 'retrieve', wrapper(cls.retrieve))

        super().__init_subclass__()

    async def retrieve(self, request, *, pk):
        return web.Response(text=f'retrieve {pk}')


class DestroyMixin:

    def __init_subclass__(cls, **kwargs):
        wrapper = cls.route(r'/{pk:\d+}', HttpMethods.DELETE)
        setattr(cls, 'delete', wrapper(cls.delete))

        super().__init_subclass__()

    async def delete(self, request, *, pk):
        return web.Response(text=f"Deleting {pk}")


class UpdateMixin:

    def __init_subclass__(cls, **kwargs):
        wrapper = cls.route(r'/{pk:\d+}', HttpMethods.PUT)
        setattr(cls, 'update', wrapper(cls.update))

        super().__init_subclass__()

    async def update(self, request, *, pk):
        return web.Response(text=f"Updating {pk}")


class CreateMixin:

    def __init_subclass__(cls, **kwargs):
        wrapper = cls.route('/', HttpMethods.POST)
        setattr(cls, 'create', wrapper(cls.create))

        super().__init_subclass__()

    async def create(self, request):
        return web.Response(text=f"Created object")
