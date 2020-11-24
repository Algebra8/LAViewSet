import sys

# aiohttp.web requires Python >= 3.7
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


__all__ = [
    'Protocol',
]
