from ..formation import _REQ_HTTP, _RES_HTTP, _CONTEXT, _REQ_DURATION


def bind_logger(ctx, logger):
    context = ctx.get(_CONTEXT, {})
    logger.bind(**context).info("context")


def context_logger(logger):
    def context_logger_middleware(ctx, next):
        bind_logger(ctx, logger)
        ctx = next(ctx)
        return ctx

    return context_logger_middleware


def async_context_logger(logger):
    async def context_logger_middleware(ctx, next):
        bind_logger(ctx, logger)
        ctx = await next(ctx)
        return ctx

    return context_logger_middleware
