from toolz import reduce

_REQ_HTTP = "fmtn.req.http"
_RES_HTTP = "fmtn.res.http"
_CONTEXT = "fmtn.context"
_SESSION = "fmtn.session"
_RETRY = "fmtn.retry"
_REQ_ID = "req.id"
_UID = "uid"
_REQ_PARENT_ID = "req.parent.id"
_REQ_DURATION = "req.duration_us"
_RES_DEFAULT_TIME_OUT = 30
_RETRY_IN_BETWEEN_CALL_SLEEP = 10


def wrap(call, middleware=None):
    if middleware is None:
        middleware = []
    return reduce(
        lambda acc, m: lambda ctx: m(ctx, acc),
        reversed(middleware),
        lambda ctx: call(ctx),
    )
