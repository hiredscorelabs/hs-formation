from urllib.parse import urljoin
from attr import attrib, attrs
import xmltodict
from aiohttp import ClientSession, ClientTimeout, BasicAuth

from .formation import (
    FormationHttpRequest, apply_params, client_decorator, get_response, wrap,
    _REQ_HTTP,
    _RES_HTTP,
    _SESSION,
    _RES_DEFAULT_TIME_OUT,
    _REQ_DURATION, BaseSender
)


__all__ = [
    "async_client",
    "async_json_response",
    "async_xmltodict_response",
    "async_text_response",
    "async_raw_response",
]


def async_client(cls):
    return client_decorator(cls, Sender)


@attrs
class FormationAIOHttpRequest(FormationHttpRequest):
    content_resolver = attrib(default=None)


def get_response_result(ctx):
    response = get_response(ctx)
    if response is None:
        return None, None, None
    return response, response.status, response.headers


async def async_raw_response(response):
    if response is not None:
        response_data = await response.read()
        response.parsed_content = response_data
    return response


async def async_json_response(response):
    if response is not None:
        response_data = await response.json(content_type=None)
        response.parsed_content = response_data
    return response


async def async_xmltodict_response(response):
    if response is not None:
        response_txt = await response.text()
        response_data = xmltodict.parse(response_txt)
        response.parsed_content = response_data
    return response


async def async_text_response(response):
    if response is not None:
        response_data = await response.text()
        response.parsed_content = response_data
    return response


class Sender(BaseSender):
    def __init__(self, middleware=None, base_uri=None, default_response_as=None):
        super().__init__(middleware, base_uri, default_response_as or async_raw_response)

    async def send(self, method, url, session_context=None, params=None, response_as=None, **kwargs):
        params = params or {}
        params = params if isinstance(params, dict) else params.to_dict()
        (url, params) = apply_params(url, params)
        request = FormationAIOHttpRequest(
            url=urljoin(self.base_uri, url),
            method=method,
            params=params,
            content_resolver=response_as or self.default_response_as,
            **kwargs
        )
        return await self.send_request(request, session_context)

    async def send_request(self, request: FormationAIOHttpRequest, session_context=None):
        ctx = {_REQ_HTTP: request}
        if session_context:
            ctx[_SESSION] = session_context
        ctx = await wrap(requests_adapter, middleware=self.middleware)(ctx)
        return get_response_result(ctx)


async def requests_adapter(ctx):
    req = ctx[_REQ_HTTP]
    auth = None
    if req.auth:
        auth = BasicAuth(req.login, req.password, encoding="latin1")
    timeout = (
        ClientTimeout(total=req.timeout)
        if req.timeout
        else ClientTimeout(total=_RES_DEFAULT_TIME_OUT)
    )
    async with ClientSession(
        headers=req.headers, cookies=req.cookies, timeout=timeout
    ) as session:
        method = getattr(session, req.method.lower())
        async with method(
            url=req.url, params=req.params, data=req.data, auth=auth, cookies=req.cookies, json=req.json
        ) as response:
            async with response:
                response = await req.content_resolver(response)
                # Compatibility with original response objects
                response.request = req
                response.status_code = response.status
                response.elapsed = ResponseElapsed(ctx)
                ctx[_RES_HTTP] = response

            return ctx


class ResponseElapsed:
    def __init__(self, ctx):
        self.ctx = ctx

    def total_seconds(self):
        return self.ctx.get(_REQ_DURATION) / 10e6
