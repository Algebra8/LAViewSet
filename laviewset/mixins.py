from aiohttp import web
from marshmallow import ValidationError

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


@make_mixin(r'/{pk:\d+}', HttpMethods.DELETE, 'delete')
class DestroyMixin:

    async def delete(self, request, *, pk):
        obj = await _get_or_404(self.model, pk)
        await obj.delete()
        return web.json_response(status=204)


@make_mixin(r'/{pk:\d+}', HttpMethods.PUT, 'update')
class UpdateMixin:

    async def update(self, request, *, pk):
        data = await request.json()
        serializer = self.get_serializer()
        model = self.model
        cleaned_data = _validate_or_raise(serializer, data)
        obj = await _get_or_404(model, pk)
        await obj.update(**cleaned_data).apply()
        resp_data = serializer.dump(obj)
        return web.json_response(data=resp_data)


@make_mixin(r'/{pk:\d+}', HttpMethods.PATCH, 'partial_update')
class PartialUpdateMixin:

    async def partial_update(self, request, *, pk):
        data = await request.json()
        serializer = self.get_serializer(partial=True)
        model = self.model
        cleaned_data = _validate_or_raise(serializer, data)
        obj = await _get_or_404(model, pk)
        await obj.update(**cleaned_data).apply()
        resp_data = serializer.dump(obj)
        return web.json_response(data=resp_data)


@make_mixin('/', HttpMethods.POST, 'create')
class CreateMixin:

    async def create(self, request):
        data = await request.json()
        serializer = self.get_serializer()
        model = self.model
        cleaned_data = serializer.load(data)
        await serializer.is_valid(cleaned_data, raise_exception=True)
        u = await model.create(**cleaned_data)
        headers = self.get_success_headers(f"{request.url}/{u.id}")
        return web.json_response(
            data=cleaned_data,
            status=201,
            headers=headers
        )

    @staticmethod
    def get_success_headers(loc: str):
        return {'Location': loc}


class SerializerMixin:

    async def is_valid(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def not_valid(self, *, msg: str = ''):
        raise web.HTTPBadRequest(text=msg)


async def _get_or_404(model, pk):
    obj = await model.query.where(
        model.id == int(pk)
    ).gino.first()
    if obj is None:
        raise web.HTTPNotFound(
            text=f'{model.__qualname__} with pk {pk} does not exist.'
        )
    return obj


def _validate_or_raise(serializer, data):
    try:
        cleaned_data = serializer.load(data)
    except ValidationError as ve:
        raise web.HTTPBadRequest(text=str(ve)) from None
    return cleaned_data
