import asyncio
from time import sleep
from random import randint

from hs_formation.for_aio_http import async_client, async_text_response
from hs_formation.middleware import (
    async_request_logger,
    async_circuit_breaker,
    async_trigger_breaker_if,
    async_timeout,
)

from tests.utils import AsyncDummyLogger


@async_client
class AsyncBreaker(object):
    logger = AsyncDummyLogger()
    base_uri = "https://example.com"
    middleware = [
        async_timeout(1),
        async_circuit_breaker(
            logger=logger, fail_max=1, name="breaker-1", reset_timeout=10
        ),
        async_trigger_breaker_if(lambda res: False if randint(0, 5) < 2 else True),
        async_request_logger(logger),
    ]
    response_as = async_text_response

    async def go(self):
        return await self.request.get("/")


#
# for this example, we're triggering an error on an HTTP OK (200) from
# example.com. With the timings set on the breaker, you'll see something
# along these lines:
#
# ok
# breaker open
# half open
# .. (timeout 10s for reseting breaker)
# breaker half-closed
# (request)
# breaker open
# half open
#
# and so on, which symbols correct operation.
#


async def main():
    async_breaker = AsyncBreaker()
    while True:
        print("requesting...")
        # (_status, _text, _headers) = await async_breaker.go()
        try:
            (_status, _text, _headers) = await async_breaker.go()
        except Exception as ex:
            # traceback.print_exc()
            print(ex.__class__)
            print("error.")
            sleep(1)
            continue
        print("ok.")
        sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
