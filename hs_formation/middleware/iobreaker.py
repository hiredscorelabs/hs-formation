from aiobreaker import CircuitBreaker, CircuitBreakerError
from aiobreaker.listener import CircuitBreakerListener
from aiobreaker.state import CircuitBreakerState
from ..formation import _CONTEXT, _RES_HTTP
from datetime import timedelta


class AsyncBreakerTriggerException(Exception):
    pass


def breaker_logger(logger):
    class LogListener(CircuitBreakerListener):
        async def state_change(self, cb, old_state, new_state):
            print(f"old_state = {old_state}, new_state = {new_state}")
            await logger.info(
                "circuitbreaker.state_changed",
                name=cb.name,
                old_state=old_state.name,
                new_state=new_state.name,
            )

    return LogListener()


def async_trigger_breaker_if(trigger):
    async def trigger_breaker_middleware(ctx, call):
        ctx = await call(ctx)
        if trigger(ctx.get(_RES_HTTP)):
            raise AsyncBreakerTriggerException
        return ctx

    return trigger_breaker_middleware


def async_circuit_breaker(
    logger, name, fail_max=3, reset_timeout=60, state_storage=None, exclude=None
):
    if exclude is None:
        exclude = []
    breaker = CircuitBreaker(
        name=name,
        listeners=[breaker_logger(logger)],
        exclude=exclude,
        fail_max=fail_max,
        timeout_duration=timedelta(
            days=0, hours=0, minutes=0, seconds=reset_timeout, milliseconds=0
        ),
        state_storage=state_storage,
    )

    async def circuit_breaker_middleware(ctx, call):
        context = ctx.get(_CONTEXT, {})
        log = await logger.bind(**context)

        if breaker.current_state == CircuitBreakerState.OPEN:
            print(f"breaker.name = {breaker.name}")
            await log.info("circuitbreaker.open", name=breaker.name)

        call = breaker(call)

        try:
            ctx = await call(ctx)
            return ctx
        except CircuitBreakerError:
            return ctx

    return circuit_breaker_middleware
