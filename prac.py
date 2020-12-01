from aiohttp import web
from laviewset import Route, HttpMethods, ViewSet
from laviewset.views import ModelViewSet


app = web.Application()
base_route = Route.create_base(app.router)


# class AViewSet(ViewSet):
#
#     route = base_route.extend('listings')
#
#     @route('/hello', HttpMethods.GET)
#     async def hey(self, request):
#         return web.Response(text='hey')

class SomeViewSet(ModelViewSet):

    route = base_route.extend('listings')

    @route('/hello', HttpMethods.GET)
    async def hey(self, request):
        return web.Response(text='hey')


web.run_app(app, host="localhost", port=8000)

# class A:
#
#     def __init_subclass__(cls, **kwargs):
#         print(f"Initing subclass A: {cls}")
#         print(hasattr(cls, 'f'))
#         return super().__init_subclass__()
#
#     def f(self):
#         ...
#
#
# class B(A):
#
#     def __init_subclass__(cls, **kwargs):
#         super().__init_subclass__()
#         print("Initing subclass B")
#
#
# class C(B): ...

# Metaclass is at compile time, while __init_subclass__ seems to be
# dynamic:

# TODO proof of dynamic vs static here

# Ideas: if __init_subclass__ is dynamic, we can replace the metaclass
# with it, and it should solve any issues.

# Otherwise, we may need to find a way to dynamically link the innards
# of the route, so that while the route object will wrap statically,
# its path will be determined dynamically, but without the user
# instantiating the class...


# The issue is not what route needs to be at compile time,
# it is the functions that need to exist.

# When we extend ModelViewSet, we are creating a new class, which
# means that the metaclass will look for any instance of the route
# decorator.

# So, what is actually happening is in this case our new class, SomeViewSet,
# is actually overridding any methods we placed previously on ModelViewSet.
