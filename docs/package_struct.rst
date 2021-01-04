Package structure
-------------------

Since :class:`ViewSets<laviewset.views.GenericViewSet>` are statically coded
(they are initialized automatically after subclassing), it is important to let
the module your :class:`app<aiohttp.web.Application>` is running in know about
each ViewSet. This is not an issue for simple projects where everything goes into
one module. For more complex projects, on the other hand, where the ViewSets may
be distributed across other sub-packages or modules, this detail is important.
While this issue can be resolved in many ways, this section offers one
of such solutions.

A solution for complex projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assume a "complex" project structure looks similar to the package hierarchy
defined below:

.. code::

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

In this project, ``package/server.py`` is designated to define and
contain ``app`` and ``base_route``.

.. code:: Python

    # package/server.py

    from aiohttp import web
    from laviewset import Route

    app = web.Application()
    base_route = Route.create_base(app.router)


    def run_server(app: web.Application) -> None:
        web.run_app(app, host='localhost', port=8000)

.. note::

    Running the server is done lazily through the function ``run_server``.
    The server should be run in a different module to avoid either the
    handlers not registering or circular imports: ``app`` needs to know about
    the ViewSets before running so either the ViewSets are imported, which leads
    to circular imports, or they are not imported and the handlers are not
    registered.


Generally each project application will have its own designated ``views.py``.
This is not necessary but is common practice.

.. code:: Python

    # package/app1/views.py

    from laviewset import ViewSet
    from ..server import base_route


    class ListingsViewSet(ViewSet):

        route = base_route.extend('listings')

        ...

    ...

.. code:: Python

    # package/app2/views.py

    from laviewset import ViewSet
    from ..server import base_route


    class SessionsViewSet(ViewSet):

        route = base_route.extend('sessions')

        ...

    ...


``package/__init__.py`` imports the modules that contain the ViewSets. The
important thing to note here is that ``server.py`` is in the same package:
``package/server.py``.

.. code:: Python

    # package/__init__.py

    # Now `server.app` knows about
    # ListingsViewSet and SessionsViewSet.
    from .app1 import views
    from .app2 import views

Finally, the web server is run using ``run_server`` and ``app.router`` contains
all the registered handlers.

.. code:: Python

    # package/__main__.py

    from .server import app, run_server

    run_server(app)

TL; DR
~~~~~~~~~~~~~~

The key takeaway here is that before running your server, ``app`` should know
about the existence of the ViewSets. ``base_route`` holds a reference to ``app.router``.
That reference is used to register the handlers defined on any ViewSet, i.e. any
ViewSet method wrapped with the
:py:meth:`@route<laviewset.routes.Route.__call__>` decorator.

If the ViewSets, or the modules that contain them, are not included in the same
package that runs the web server, then Python will not execute the code that
contains the registration in time. That is, ``app`` will not know about the
handlers before the server is started.

