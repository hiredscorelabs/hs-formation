from toolz import merge
from ..formation import _REQ_HTTP, _REQ_ID
from uuid import uuid4


def update_req_for_req_id(ctx, key: str, idgen) -> None:
    headers = ctx[_REQ_HTTP].headers
    ctx[_REQ_HTTP].headers = merge(headers, {key: headers.get(key, str(idgen()))})
    ctx[_REQ_ID] = ctx[_REQ_HTTP].headers[key]


def request_id(key="x-request-id", idgen=uuid4):
    def request_id_middleware(ctx, next):
        update_req_for_req_id(ctx, key, idgen)
        ctx = next(ctx)
        return ctx

    return request_id_middleware


def async_request_id(key="x-request-id", idgen=uuid4):
    async def request_id_middleware(ctx, next):
        update_req_for_req_id(ctx, key, idgen)
        ctx = await next(ctx)
        return ctx

    return request_id_middleware
