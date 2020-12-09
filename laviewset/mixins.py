from aiohttp import web
from .http_meths import HttpMethods


# Credit to SO user ShadowRanger:
# https://stackoverflow.com/questions/65205205/patching-init-subclass
def _make_patched_initsubclass_for(
        __class__, *, path, method, handler_name
):

    def _patched_initsubclass(cls, **kwargs):
        wrapper = cls.route(path, method)
        setattr(
            cls, handler_name,
            wrapper(getattr(cls, handler_name))
        )
        super().__init_subclass__(**kwargs)
    return classmethod(_patched_initsubclass)


def make_mixin(path, method, handler_name):
    """
    Decorator to convert a class into a ViewSet Mixin.
    """

    # A key element of ViewSet mixins is the existence of
    # __init_subclass__ which ensures all mixins in the mro
    # properly define the needed view and pass on that responsibility
    # to whatever other mixin might exist on the extended class.

    def mixin_wrapper(cls):
        cls.__init_subclass__ = _make_patched_initsubclass_for(
            cls,
            path=path,
            method=method,
            handler_name=handler_name
        )
        return cls

    return mixin_wrapper


@make_mixin('/', HttpMethods.GET, 'list')
class ListMixin:

    async def list(self, request):
        db = self.get_db()
        l = await db.all(self.model.query)
        serializer = self.get_serializer()
        return web.json_response(serializer(l))


@make_mixin(r'/{pk:\d+}', HttpMethods.GET, 'retrieve')
class RetrieveMixin:

    async def retrieve(self, request, *, pk):
        r = await self.model.query.where(
            self.model.id == int(pk)
        ).gino.first()
        serializer = self.get_serializer()
        return web.json_response(serializer(r))


@make_mixin(r'/{pk:\d+}', HttpMethods.DELETE, 'delete')
class DestroyMixin:

    async def delete(self, request, *, pk):
        return web.Response(text=f"Deleting {pk}")


@make_mixin(r'/{pk:\d+}', HttpMethods.PUT, 'update')
class UpdateMixin:

    async def update(self, request, *, pk):
        return web.Response(text=f"Updating {pk}")


@make_mixin('/', HttpMethods.POST, 'create')
class CreateMixin:

    async def create(self, request):
        return web.Response(text=f"Created object")
