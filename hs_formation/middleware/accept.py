from toolz import merge
from ..formation import _REQ_HTTP


def update_req_for_mime_type(ctx, mime_type):
    req = ctx.get(_REQ_HTTP)
    req.headers = merge(req.headers, {"Content-Type": mime_type})


def accept(mime_type):
    def accept_middleware(ctx, call):
        update_req_for_mime_type(ctx, mime_type)
        return call(ctx)

    return accept_middleware


def async_accept(mime_type):
    async def accept_middleware(ctx, call):
        update_req_for_mime_type(ctx, mime_type)
        return await call(ctx)

    return accept_middleware
