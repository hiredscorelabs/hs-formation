import asyncio

from hs_formation.for_aio_http import async_client, async_json_response
from hs_formation.middleware import (
    async_request_logger,
    async_ua,
    async_accept,
    async_timeout,
)


from tests.utils import AsyncDummyLogger


@async_client
class AsyncHttpBin(object):
    base_uri = "https://httpbin.org"
    middleware = [
        async_timeout(0.1),
        async_accept("application/json"),
        async_ua("the-fabricator/1.0.0"),
        async_request_logger(AsyncDummyLogger()),
    ]
    response_as = async_json_response

    async def publish(self, data):
        return await self.request.post("post", data=data)


async def main():
    data = {"key1": ["value1", "value2"]}
    httpbin = AsyncHttpBin()
    try:
        (resp, _, _) = await httpbin.publish(data)
        print(resp.parsed_content)
        print("if you see this, you have a very fast internet")
    except:
        print("call timed out, which is OK because timeout is 100ms")


if __name__ == "__main__":
    asyncio.run(main())
