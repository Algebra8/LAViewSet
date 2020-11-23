### LAViewSet 
#### A Lyte (light) Asynchronous ViewSet.

A ViewSets package, a-la Django Rest Framework - ViewSets, built on top of 
`aiohttp.web`.
# *********************************************************


### Getting Started

---

#### Quick Start

```
# laviewset_intro.py

from aiohttp import web
from laviewset import Route, ViewSet, HttpMethods

app = web.Application()
base_route = Route.create_base(app.router)      # '/'


class ListingsViewSet(ViewSet):
    
    route = base_route.extend('listings')  # '/listings'

    @route('/', HttpMethods.GET)
    async def list(self, request):
        assert isinstance(request, web.Request)
        return web.Response(text='GET at '/listings')


web.run_app(app)
```

For a step-by-step walkthrough, continue reading below. 

Or, [skip ahead](#cheatsheet) for a
more thorough look at fully extending `laviewset.ViewSet`.

___

#### Intro
The first step is to create a **base route** by passing the `aiohttp.web.UrlDispatcher` of your 
current application into `Route.create_base`:

```
# laviewset_intro.py

from aiohttp import web
from laviewset import Route

app = web.Application()
base_route = Route.create_base(app.router)      # '/'
```

`base_route` can then be extended into resources that you want to include in your ViewSets:

```
listings_route = base_route.extend('listings')  # '/listings'
events_route = base_route.extend('/events')     # '/events'

# We can further extend a resource
sessions_route = listings.extend('sessions')    # '/listings/sessions'
```

Now that we have the resource we want a ViewSet to manage, we can create our ViewSet. This is done 
by subclassing `laviewset.ViewSet`, including your route as the `route` attribute, and overriding 
the ViewSet methods and/or including your custom views:

```
# laviewset_intro.py

from aiohttp import web
from laviewset import Route, ViewSet, HttpMethods

app = web.Application()
base_route = Route.create_base(app.router)      # '/'


class ListingsViewSet(ViewSet):
    
    route = base_route.extend('listings')  # '/listings'
    serializer = 'some_serializer'

    @route('/', HttpMethods.GET)
    async def list(self, request):
        ...
        return web.Response(text='GET at /listings with {self.serializer}')


web.run_app(app)
```

Note, the code above is similar to the following:

```
from aiohttp import web


serializer = 'some_serializer'

def handler(request):
    ...
    return web.Response(text='GET at /listings with {self.serializer}')


app = web.Application()
app.add_routes([web.get('/', handler)])
web.run_app(app)
```

___

#### ViewSet methods

##### @route decorator
In order to create a view on the ViewSet, the `@route` decorator is required. Since each view 
is essentially a wrapper over [`aiohttp.web.route`](https://github.com/aio-libs/aiohttp/blob/master/aiohttp/web_routedef.py#L105), 
the arguments passed into the decorator 
 correlate with the arguments for `web.route`: the first argument is the `path`, 
 the second argument is the HTTP method for the view (`method`),
any other keyword argument passed into the decorator will be included as `kwargs` to 
the `web.route` method, and finally, the view itself will be the `handler`.

```
    @route('/', HttpMethods.GET, z=20, f='abc')     # z=20 and f='abc' will be
    async def list(self, request):                  # passed into web.route
        ...
        return web.Response(text='GET at '/listings')
```

Since the idea behind `laviewset` is an asynchronous ViewSet a-la [Django Rest Framework - ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/), 
the methods `list`, `create`, `retrieve`, `update`, `partial_update`, and `delete` are included on 
the base class `laviewset.ViewSet`. However, unlike Rest Framework, they are not complete: the user still needs 
to declare the view using the `@route` decorator. One reason for this design decision is to allow more flexibility to the 
user, e.g. to decide on what `kwargs` to pass into `web.route`. Trying to access any of the aforementioned methods 
without overriding and completing them will return a `404NotFound`.

##### View method signatures
The signatures of the views are important. Each view signature requires at least the `self` and `request` arguments. 
The `request` is in fact a `web.Request` object, and can be accessed as such: `request.query`, `request.rel_url`, etc
 are all accessible. If the `path` declared in the `@route` decorator is a 
[variable path](https://docs.aiohttp.org/en/stable/web_quickstart.html#variable-resources), then the `{identifier}` should 
be included in the view signature as a `KEYWORD_ONLY` argument **and** have the same name as the 
identifier included in the path, otherwise an `laviewset.ViewSignatureError` will be raised:

```
# Correct

    @route(r'/{pk:\d+}', HttpMethods.GET)  # /listings/123
    async def retrieve(self, request, *, pk):   # `pk` is KEYWORD_ONLY and
        assert pk == 123                        # `pk` is same as identifier
        return web.Response(text=f'retrieved {pk}')

# Incorrect

    @route(r'/{pk:\d+}', HttpMethods.GET)
    async def retrieve(self, request, pk):      # `pk` is not KEYWORD_ONLY
        ...
        return web.Response(text=f'retrieved {pk}')

# Incorrect

    @route(r'/{fk:\d+}', HttpMethods.GET)
    async def retrieve(self, request, *, pk):  # `pk` != `fk`
        ...
        return web.Response(text=f'retrieved {pk}')

```

___ 

##### Custom views

Custom views can also be defined. Simply wrap a method with the `@route` decorator
and follow the rules described above:

```
    # Custom GET view
    # '/listings/123/events/Coachella'
    @route(r'/{pk:\d+}/events/{name:\w+}', HttpMethods.GET)
    async def custom_get(self, request, *, pk, name):
        assert pk == 123
        assert name == 'Coachella'
        return web.Response(text=f'GET at /listings/{pk}/events/{name}')

    # Custom DELETE view
    # '/listings/custom_delete/123/Coachella'
    @route(r'/custom_delete/{pk:\d+}/{name:\w+}', HttpMethods.DELETE)
    async def custom_delete(self, request, *, pk, name):
        assert pk == 123
        assert name == 'Coachella'
        return web.Response(text=f'Deleting something to do with {pk} {name}')
```

> **_A short note on errors:_**  
> All `laviewset` errors are raised "statically", i.e. before your server is up and running. 

___

#### Project structure

Since ViewSets do not need to be initialized, it is important to let the module your app is 
running in know about each `ViewSet`. Therefore, for more complex project structures, the following
structure is recommended:

```
proj/
├── package/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py
│   ├── app1/
│   │   └── views.py
│   └── app2/
│       └── views.py
├── conf.py
└── README.md
```

```
# package/server.py

from aiohttp import web
from laviewset import Route

app = web.Application()
base_route = Route.create_base(app.router)


def run_server(app: web.Application) -> None:
    web.run_app(app, host='localhost', port=8000)

```

```
# package/app1/views.py

from laviewset import ViewSet
from ..server import base_route
...
```

```
# package/app2/views.py

from laviewset import ViewSet
from ..server import base_route
...
```

```
# package/__init__.py

# Now `server.app` knows about `ViewSet`s.
from .app1 import views
from .app2 import views
```

```
# package/__main__.py

from .server import app, run_server

run_server(app)
```

# *********************************************************

### [Cheatsheet](#cheatsheet)
```
# quicksetup.py

from aiohttp import web
from laviewset import Route, ViewSet, HttpMethods

app = web.Application()
base_route = Route.create_base(app.router)


class ListingsViewSet(ViewSet):
    
    route = base_route.extend('listings')  # '/listings'
    
    @route('/', HttpMethods.GET)
    async def list(self, request):
        # GET at '/listings'
        ...
        return web.Response(...)

    @route(r'/{pk:\d+}', HttpMethods.GET)
    async def retrieve(self, request, *, pk):
        # GET at '/listings/{pk}'
        # where the dynamic value {pk} can be accessed 
        # through `pk`.
        ...
        return web.Response(...)
    
    @route('/', HttpMethods.POST)
    async def create(self, request):
        # POST at '/listings'
        data = await request.json()
        return web.Response(text=f'Metrics Created data: {data}')

    @route(r'/{pk:\d+}', HttpMethods.DELETE)
    async def delete(self, request, *, pk):
        # DELETE at '/listings/{pk}'
        ...
        return web.Response(...)

    @route(r'/{pk:\d+}', HttpMethods.PUT)
    async def update(self, request, *, pk):
        # PUT at '/listings/{pk}'
        ...
        return web.Response(...)

    @route(r'/{pk:\d+}', HttpMethods.PATCH)
    async def partial_update(self, request, *, pk):
        # PATCH at '/listings/{pk}'
        ...
        return web.Response(...)

    @route(r'/{pk:\d+}/do_thing/{name:\w+}', HttpMethods.GET)
    async def custom_view(self, request, *, pk, name):
        # GET at '/listings/{pk}/do_thing/{name}'
        ...
        return web.Response(...)
```

# *********************************************************

### Requirements

* Python >= 3.8
* aiohttp==3.6.2

# *********************************************************

### Installation

This package does not exist on PyPI yet, so the only way to 
install it is through `LAViewSet/setup.py`.

# *********************************************************

### License
`laviewset` is offered under the MIT license. 

 This package uses the [`aiohttp`](https://github.com/aio-libs/aiohttp) package, which is distributed under the Apache 2 license.




