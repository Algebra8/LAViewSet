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

