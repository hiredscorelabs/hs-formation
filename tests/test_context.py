import pytest
import pydash

from hs_formation.for_requests import build_sender
from hs_formation import _CONTEXT
from hs_formation.middleware import context

@pytest.mark.vcr()
def test_namespace():
    expected = 'formation-namespace'
    sender = build_sender(middleware=[
        assert_context(expected),
        context(env='env', namespace=expected),
    ])
    sender("get", "http://example.com")
    sender = build_sender(middleware=[
        assert_context(expected),
        context(env='env', namespace=expected),
    ])


def assert_context(expected_namespace):
    def _inner(ctx, _next):
        ctx = _next(ctx)
        actual = pydash.get(ctx, [_CONTEXT, 'ns'])
        assert actual == expected_namespace
        return ctx

    return _inner
