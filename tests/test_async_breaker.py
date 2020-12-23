import pytest
from .utils import AsyncDummyLogger
from hs_formation.middleware import (
    async_circuit_breaker,
    async_trigger_breaker_if,
    AsyncBreakerTriggerException,
)


async def malfunction(ctx):
    print(f"In malfunction")
    raise Exception("malfunction exception")


async def force_run(cb):
    try:
        await cb({}, malfunction)
    except:  # noqa
        pass


async def do_nothing(ctx):
    return {}


@pytest.mark.asyncio
async def test_async_trigger():
    t = async_trigger_breaker_if(lambda res: True)
    try:
        await t({}, do_nothing)
        pytest.fail("should throw")
    except AsyncBreakerTriggerException as ex:
        pass


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_circuit_breaker_middleware(snapshot):
    logger = AsyncDummyLogger()
    cb = async_circuit_breaker(logger, "test-cb")
    await force_run(cb)
    await force_run(cb)
    await force_run(cb)
    await force_run(cb)
    await force_run(cb)
    await force_run(cb)
    await force_run(cb)

    snapshot.assert_match(logger.messages)
