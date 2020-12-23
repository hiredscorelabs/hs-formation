from ..formation import _RETRY, _RETRY_IN_BETWEEN_CALL_SLEEP
from time import sleep
import asyncio


def retry(max_retries=3, retry_in_between_call_sleep=_RETRY_IN_BETWEEN_CALL_SLEEP):
    def retry_middleware(ctx, call):
        try:
            res = call(ctx)
            return res
        except Exception as ex:
            retries = ctx.get(_RETRY, 0)
            if retries >= max_retries - 1:
                raise ex
            ctx[_RETRY] = 1 + retries
            # TODO exponential backoff
            sleep(retry_in_between_call_sleep)
            res = retry_middleware(ctx, call)
            return res

    return retry_middleware


def async_retry(
    max_retries=3, retry_in_between_call_sleep=_RETRY_IN_BETWEEN_CALL_SLEEP
):
    async def retry_middleware(ctx, call):
        try:
            res = await call(ctx)
            return res
        except Exception as ex:
            retries = ctx.get(_RETRY, 0)
            if retries >= max_retries - 1:
                raise ex
            ctx[_RETRY] = 1 + retries
            # TODO exponential backoff
            await asyncio.sleep(retry_in_between_call_sleep)
            res = await retry_middleware(ctx, call)
            return res

    return retry_middleware
