from .breaker import (
    circuit_breaker,
    trigger_breaker_if,
    BreakerTriggerException,
)  # noqa

from .iobreaker import (
    async_circuit_breaker,
    async_trigger_breaker_if,
    AsyncBreakerTriggerException,
)  # noqa

from .context import context, async_context
from .context_logger import context_logger, async_context_logger  # noqa
from .logger import request_logger, async_request_logger
from .request_duration import request_duration, async_request_duration
from .request_id import request_id, async_request_id
from .retry import retry, async_retry  # noqa
from .ua import ua, async_ua  # noqa
from .accept import accept, async_accept  # noqa
from .timeout import timeout, async_timeout  # noqa


def default_stack(logger):
    return [request_id(), context(), request_duration(), request_logger(logger)]
