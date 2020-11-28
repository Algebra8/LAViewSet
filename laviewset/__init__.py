from typing import Tuple

from .routes import Route
from .views import ViewSet, HttpMethods
from .resources import rfc

__all__: Tuple[str] = (
    'Route',
    'ViewSet',
    'HttpMethods',
    'rfc'
)

__version__ = "0.0.1"

__author__ = "Milad M. Nasrollahi"
__email__ = "milad.m.nasr@gmail.com"
