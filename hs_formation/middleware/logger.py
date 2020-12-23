from ..formation import (
    _REQ_HTTP,
    _RES_HTTP,
    _CONTEXT,
    _REQ_DURATION,
    _RES_HTTP_HEADERS,
    _RES_HTTP_STATUS_CODE,
    _RES_HTTP_CONTENT_LENGTH,
)
from toolz.curried import valfilter


def request_logger(logger):
    no_nones = valfilter(lambda x: x)

    def request_logger_middleware(ctx, next):
        req = ctx[_REQ_HTTP]
        context = ctx.get(_CONTEXT, {})
        msg = "request.http"

        log = logger.bind(**context)
        log.info(msg, url=req.url, method=req.method, params=no_nones(req.params))
        log.debug(msg, headers=req.headers)

        ctx = next(ctx)

        res = ctx[_RES_HTTP]

        msg = "response.http"
        log.info(
            msg,
            url=res.request.url,
            status=res.status_code,
            method=res.request.method,
            elapsed=res.elapsed,
            size=len(res.content),
            duration_us=ctx.get(_REQ_DURATION, None),
        )
        log.debug(msg, headers=res.headers)
        return ctx

    return request_logger_middleware


def async_request_logger(logger):
    no_nones = valfilter(lambda x: x)

    async def request_logger_middleware(ctx, next):
        req = ctx[_REQ_HTTP]
        context = ctx.get(_CONTEXT, {})
        msg = "before request.http"

        log = await logger.bind(**context)
        await log.info(msg, url=req.url, method=req.method, params=no_nones(req.params))
        await log.debug(msg, headers=req.headers)

        ctx = await next(ctx)

        msg = "after response.http"
        await log.info(
            msg,
            url=req.url,
            status=ctx.get(_RES_HTTP_STATUS_CODE),
            method=req.method,
            elapsed=ctx.get(_REQ_DURATION, None),
            size=ctx.get(_RES_HTTP_CONTENT_LENGTH),
            duration_us=ctx.get(_REQ_DURATION, None),
        )
        await log.debug(msg, headers=ctx.get(_RES_HTTP_HEADERS))
        return ctx

    return request_logger_middleware
