from ..formation import _REQ_HTTP


def update_req_for_timeout(ctx, timeout) -> None:
    req = ctx.get(_REQ_HTTP)
    if timeout:
        req.timeout = timeout


def timeout(timeout=None):
    def timeout_middleware(ctx, call):
        update_req_for_timeout(ctx, timeout)
        return call(ctx)

    return timeout_middleware


def async_timeout(timeout=None):
    async def timeout_middleware(ctx, call):
        update_req_for_timeout(ctx, timeout)
        return await call(ctx)

    return timeout_middleware
