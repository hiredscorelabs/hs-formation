import datetime
import math
import asyncio

from ..formation import _REQ_DURATION

SEC_TO_MICROSEC = 1e6


def request_duration(now=datetime.datetime.now):
    def request_duration_middleware(ctx, next):
        start = now()
        ctx = next(ctx)
        end = now() - start
        ctx[_REQ_DURATION] = math.floor(end.total_seconds() * SEC_TO_MICROSEC)
        return ctx

    return request_duration_middleware


def async_request_duration():
    async def request_duration_middleware(ctx, next):
        start = asyncio.get_event_loop().time()
        ctx = await next(ctx)
        end = asyncio.get_event_loop().time() - start
        ctx[_REQ_DURATION] = math.floor(end * SEC_TO_MICROSEC)
        return ctx

    return request_duration_middleware
