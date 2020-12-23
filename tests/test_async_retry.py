import pytest
from hs_formation.for_aio_http import async_client, async_json_response
from hs_formation.middleware import async_retry


def snap(resp_tuple):
    return (resp_tuple[0], resp_tuple[1], sorted(resp_tuple[2].items()))


def async_fail(times):
    async def fail_middleware(ctx, call):
        t = ctx.get("fail", times)
        t = t - 1
        if t <= 0:
            return await call(ctx)
        else:
            ctx["fail"] = t
            raise RuntimeError("something is wrong")

    return fail_middleware


@async_client
class HttpBinNice(object):
    base_uri = "https://httpbin.org"
    middleware = [
        async_retry(max_retries=2, retry_in_between_call_sleep=1),
        async_fail(1),
    ]
    response_as = async_json_response

    async def get(self):
        return await self.request.get("get")


@async_client
class HttpBinBad(object):
    base_uri = "https://httpbin.org"
    middleware = [
        async_retry(max_retries=2, retry_in_between_call_sleep=1),
        async_fail(3),
    ]
    response_as = async_json_response

    async def get(self):
        return await self.request.get("get")


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_retry(snapshot):
    c = HttpBinNice()
    snapshot.assert_match(await c.get())


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_retry_fails(snapshot):
    c = HttpBinBad()

    try:
        await c.get()
        pytest.fail("should actually fail")
    except RuntimeError as ex:
        pass
