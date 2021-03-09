from hs_formation.for_aio_http import Sender, apply_params
from hs_formation.middleware import ua, accept
import pytest


@pytest.mark.asyncio
async def test_async_apply_params(snapshot):
    snapshot.assert_match(
        apply_params(
            "http://github.com/:user/:repo?q=foobar",
            {":user": "jondot", ":repo": "formation", "foobar": "foobaz"},
        )
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_for_requests():
    sender = Sender(middleware=[])
    await sender.get("http://example.com")


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_for_requests_with_params():
    sender = Sender(middleware=[])
    await sender.get(
        "http://example.com",
        headers={"x-custom": "hello"},
        params={"v": "1.0"},
        data="some-data",
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_ua():
    sender = Sender(middleware=[ua("foobar/1.0.0")])
    await sender.get("http://example.com", headers={"x-custom": "hello"}, params={"v": "1.0"})


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_accept():
    sender = Sender(middleware=[accept("application/json")])
    await sender.get("http://example.com", headers={"x-custom": "hello"}, params={"v": "1.0"})


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_cookies():
    sender = Sender(middleware=[])
    await sender.get(
        "http://example.com",
        headers={"x-custom": "hello"},
        params={"v": "1.0"},
        cookies={"clientSession": "session"},
    )
