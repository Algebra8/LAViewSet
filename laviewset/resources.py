from __future__ import annotations

from typing import Callable, NamedTuple
from enum import Enum


def strict_build(p: str):
    # Append leading slash to all in u
    # then append the trailing slash to
    # the result.
    result = ''
    u = [r for r in p.split('/') if r]
    for path in u:
        result += f'/{path}'
    return result + '/'


def non_strict_build(p):
    # Append leading slash to all in u
    # and then append them.
    result = ''
    u = [r for r in p.split('/') if r]
    for path in u:
        result += f'/{path}'
    return result


class Rfc(Enum):

    STRICT = 'strict'
    NON_STRICT = 'non_strict'
    COL = 'collection'
    SUB = 'subordinate'
    EMPTY = 'empty'

    @classmethod
    def get_build(cls, rfc: Rfc) -> [Callable[[str], str]]:
        if cls(rfc) is cls.STRICT:
            return strict_build
        elif cls(rfc) is cls.NON_STRICT:
            return non_strict_build
        else:
            # We return an identity function so
            # no type checking is required by caller.
            return lambda p: p


class ResourceError(ValueError):

    ...


class Resource:
    """
    A resource builder class.

    The URI's `scheme` and `authority` will be handled
    by aiohttp. The Resource class only cares about `path`,
    `query`, and `fragment`s.
    """
    path: str
    enforce: Rfc
    res_type: Rfc

    def __init__(self, path, *, enforce=None, res_type=None):
        self.path = path
        self.enforce = enforce if enforce is not None else Rfc.NON_STRICT
        self.res_type = res_type if res_type is not None else Rfc.EMPTY
        self.build_strategy = Rfc.get_build(self.enforce)

    @classmethod
    def create_base(cls, *, enforce=None) -> Resource:
        base = cls('/', enforce=enforce)
        base.build()
        return base

    def build(self) -> None:
        """Build the resource."""
        self.path = self.build_strategy(self.path)

    def __add__(self, other) -> Resource:
        """Add two resources together.

        Policies go upstream, meaning `other`'s policies
        are used in the Resource that is to be returned.

        The caller should expect a built resource.
        """
        new_resource = Resource(
            self.path + other.path,
            enforce=other.enforce,
            res_type=other.res_type
        )
        new_resource.build()
        return new_resource

    def __str__(self):
        return self.path

    def extend(self, path, *, enforce=None) -> Resource:
        """Extend an already existing resource.

        Enforcement can be overridden in call to extend by
        passing `enforce`, otherwise self's `enforce` will be
        used.
        """
        if enforce is None:
            enforce = self.enforce

        extended = Resource(
            self.path + path,
            enforce=enforce,
        )
        extended.build()
        return extended

    def leaf(self, path, *, res_type=None):
        """Extend an already existing resource into a leaf.

        The leaf resource can no longer be extended or
        added on to, and will act as the final actionable
        endpoint for a given resource.
        """
        leaf = Resource(
            self.path + path,
            enforce=self.enforce,
            res_type=res_type
        )
        leaf.build()
        leaf._validate_leaf()
        return leaf

    def _validate_leaf(self) -> None:
        """Validate the policy and resource type
        of a leaf Resource.

        For example, if a STRICT policy is used, check
        to make sure a Resource Type is given and make the
        necessary modification.

        Side-effects:
            - will modify path if STRICT, SUBORDINATE
            combo are used.
            - will raise TypeError for STRICT, EMPTY or
            NON-STRICT, ~EMPTY
        """
        enforce = Rfc(self.enforce)
        res_type = Rfc(self.res_type)

        if enforce is Rfc.STRICT:
            self._validate_strict(res_type)
        elif enforce is Rfc.NON_STRICT:
            self._validate_non_strict(res_type)

    def _validate_strict(self, res_type):
        """Validate a STRICT, `res_type` combo.

        Side-effects:
            - may modify path
            - may raise TypeError
        """
        if res_type is Rfc.EMPTY:
            raise TypeError("Must set resource type  STRICT.")
        if res_type is Rfc.SUB:
            self.path = self.path[:-1]

    @staticmethod
    def _validate_non_strict(res_type):
        """Validate a NON-STRICT, `res_type` combo.

        Side-effects:
            - may raise TypeError
        """
        if res_type is not Rfc.EMPTY:
            raise TypeError("Don't set a resource type when NON-STRICT.")


class RfcInterface(NamedTuple):

    strict = Rfc.STRICT
    non_strict = Rfc.NON_STRICT
    collection = Rfc.COL
    subordinate = Rfc.SUB


rfc = RfcInterface()
