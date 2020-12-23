from toolz import merge
from ..formation import _REQ_HTTP


def update_header_for_ua(ctx, user_agent: str) -> None:
    req = ctx.get(_REQ_HTTP)
    req.headers = merge(req.headers, {"User-Agent": user_agent})


def ua(user_agent="formation/1.0.0"):
    def ua_middleware(ctx, call):
        update_header_for_ua(ctx, user_agent)
        return call(ctx)

    return ua_middleware


def async_ua(user_agent="formation/1.0.0"):
    async def ua_middleware(ctx, call):
        update_header_for_ua(ctx, user_agent)
        return await call(ctx)

    return ua_middleware
