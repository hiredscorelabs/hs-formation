import datetime
from urllib.parse import urljoin
from attr import attrib, attrs
from toolz.curried import keyfilter, reduce
import xmltodict
from aiohttp import ClientSession, ClientTimeout, BasicAuth

from .formation import (
    wrap,
    _REQ_HTTP,
    _RES_HTTP,
    _SESSION,
    _RES_DEFAULT_TIME_OUT,
    _REQ_DURATION
)


__all__ = [
    "build_sender",
    "build",
    "async_client",
    "async_json_response",
    "async_xmltodict_response",
    "async_text_response",
    "async_raw_response",
]


def async_client(cls=None):
    def client_decorator(cls):
        original_init = cls.__init__

        def now_iso(self):
            return datetime.datetime.utcnow().isoformat()

        def path(self, p):
            return urljoin(self.base_uri, p)

        def init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            base_uri = kwargs.get(
                "base_uri", getattr(self.__class__, "base_uri", "http://localhost")
            )
            response_as = kwargs.get(
                "response_as", getattr(self.__class__, "response_as", None)
            )
            self.request = build(
                middleware=kwargs.get(
                    "middleware", getattr(self.__class__, "middleware", [])
                ),
                base_uri=base_uri,
                response_as=response_as,
            )

            self.base_uri = base_uri

        cls.path = path
        cls.now_iso = now_iso
        cls.__init__ = init
        return cls

    if cls:
        return client_decorator(cls)
    return client_decorator


@attrs
class FormationAIOHttpRequest:
    url = attrib()
    method = attrib(default="get")

    # these two are very stabby. a single default instance is shared among all attrs
    # objects. to assign new keys, update immutably -- use merge and re-assign
    headers: dict = attrib(default={})
    cookies: dict = attrib(default={})
    params: dict = attrib(default={})

    auth: dict = attrib(default=None)
    data = attrib(default=None)
    files = attrib(default=None)
    json = attrib(default=None)
    timeout = attrib(default=None)
    allow_redirects: bool = attrib(default=True)
    content_resolver = attrib(default=None)


def params_filter(p):
    return p.startswith(":")


def not_params_filter(p):
    return not params_filter(p)


def apply_params(url, params):
    route_params = keyfilter(params_filter, params)
    return (
        reduce(lambda acc, kv: acc.replace(kv[0], kv[1]), route_params.items(), url),
        keyfilter(not_params_filter, params),
    )


def get_response(ctx):
    return ctx.get(_RES_HTTP, None)


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
        response_data = await response.json()
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


def build_sender(
    middleware=None, base_uri=None, default_response_as=async_raw_response
):
    if middleware is None:
        middleware = []
    wrapped = wrap(requests_adapter, middleware=middleware)

    async def sender(
        method,
        url,
        session_context=None,
        params=None,
        response_as=default_response_as,
        **kwargs
    ):
        params = params or {}
        params = params if isinstance(params, dict) else params.to_dict()
        (url, params) = apply_params(url, params)
        req = FormationAIOHttpRequest(
            url=urljoin(base_uri, url),
            method=method,
            params=params,
            content_resolver=response_as,
            **kwargs
        )
        ctx = {_REQ_HTTP: req, _SESSION: session_context or {}}
        ctx = await wrapped(ctx)
        return get_response_result(ctx)

    return sender


class Sender(object):
    def __init__(self, send):
        self.send = send

    async def get(self, path, **kwargs):
        return await self.send("get", path, **kwargs)

    async def post(self, path, **kwargs):
        return await self.send("post", path, **kwargs)

    async def put(self, path, **kwargs):
        return await self.send("put", path, **kwargs)

    async def delete(self, path, **kwargs):
        return await self.send("delete", path, **kwargs)


def build(middleware=None, base_uri=None, response_as=None):
    if middleware is None:
        middleware = []
    return Sender(
        build_sender(
            middleware=middleware, base_uri=base_uri, default_response_as=response_as
        )
    )


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
            url=req.url, params=req.params, data=req.data, auth=auth, cookies=req.cookies,
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
