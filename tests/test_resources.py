import pytest

import mock

from laviewset import rfc
from laviewset.resources import (
    non_strict_build,
    strict_build,
    Resource
)


def test_strict_build():
    base = ''
    listings = '/listings'
    sessions = '/sessions'

    assert strict_build(base) == '/'
    assert strict_build(base + listings) == '/listings/'
    assert (
            strict_build(base + listings + sessions)
            == '/listings/sessions/'
    )


def test_non_strict_build():
    base = ''
    listings = '/listings'
    sessions = '/sessions'

    assert non_strict_build(base) == ''
    assert non_strict_build(base + listings) == '/listings'
    assert (
        non_strict_build(base + listings + sessions)
        == '/listings/sessions'
    )


def test_create_base():
    base_0 = Resource.create_base()  # default
    base_1 = Resource.create_base(enforce=rfc.strict)

    assert base_0.path == ''
    assert base_0.enforce == rfc.non_strict

    assert base_1.path == '/'
    assert base_1.enforce == rfc.strict


@mock.patch('laviewset.resources.non_strict_build')
@mock.patch('laviewset.resources.strict_build')
def test_build(mock_strict_build, mock_non_strict_build):
    url = 'listings/sessions'
    # Build occurs with main api interaction
    # such as: create_base, extend, and leaf.
    # Since we are just testing build, we directly
    # init a Resource.
    r_0 = Resource(path=url)    # default enforcement
    r_1 = Resource(path=url, enforce=rfc.strict)

    r_0.build()
    mock_non_strict_build.assert_called_once_with(url)

    r_1.build()
    mock_strict_build.assert_called_once_with(url)


# When testing for enforcement and builds on extensions,
# leaves, and even bases, it suffices to assert the
# correct enforcement type as well as a call to `Resource.build`.
# In fact this may be preferable to directly testing the resulting
# path.
def test_extend_strict():
    r_strict = Resource.create_base(enforce=rfc.strict)

    with mock.patch.object(Resource, 'build') as mb_strict:
        # No need to override enforcement since enforcement
        # for extension is same as parent, i.e. strict.
        extended_strict = r_strict.extend('listings')
    mb_strict.assert_called_once_with()
    assert extended_strict.enforce == rfc.strict

    with mock.patch.object(Resource, 'build') as mb_non_strict:
        # Here, we **do** need to override enforcement since
        # extension's enforcement is different from parent.
        extended_non_strict = r_strict.extend(
            'sessions', enforce=rfc.non_strict
        )
    mb_non_strict.assert_called_once_with()
    assert extended_non_strict.enforce == rfc.non_strict


def test_extend_non_strict():
    r_non_strict = Resource.create_base()

    extended_non_strict = r_non_strict.extend('listings')
    assert extended_non_strict.path == '/listings'
    assert extended_non_strict.enforce == rfc.non_strict

    extended_strict = r_non_strict.extend('sessions', enforce=rfc.strict)
    assert extended_strict.path == '/sessions/'
    assert extended_strict.enforce == rfc.strict


@pytest.fixture
def strict_extension():
    r = Resource.create_base()
    return r.extend('listings', enforce=rfc.strict)


@pytest.fixture
def non_strict_extension():
    r = Resource.create_base()
    return r.extend('listings')


def test_leaf_strict_success(strict_extension):
    col = strict_extension.leaf('/sessions', res_type=rfc.collection)
    assert col.path == '/listings/sessions/'

    sub = strict_extension.leaf('pk', res_type=rfc.subordinate)
    assert sub.path == '/listings/pk'


def test_leaf_strict_fail(strict_extension):
    with pytest.raises(TypeError):
        strict_extension.leaf('/sessions')


def test_leaf_non_strict_success(non_strict_extension):
    leaf_0 = non_strict_extension.leaf('/sessions')
    assert leaf_0.path == '/listings/sessions'

    leaf_1 = non_strict_extension.leaf('/pk')
    assert leaf_1.path == '/listings/pk'


def test_leaf_non_strict_fail(non_strict_extension):
    with pytest.raises(TypeError):
        non_strict_extension.leaf('sessions', res_type=rfc.collection)



