from abc import ABC, abstractmethod
from collections.abc import Iterable
import requests
from urllib.parse import urljoin
from .formation import FormationHttpRequest, apply_params, client_decorator, get_response, wrap, _REQ_HTTP, _RES_HTTP, \
    _SESSION, BaseSender
from lxml import html
import xmltodict

__all__ = [
    "client",
    "raw_response",
    "json_response",
    "xmltodict_response",
    "html_response",
    "text_response",
]


def client(cls):
    return client_decorator(cls, Sender, SessionSender)


def _raw_response(ctx):
    res = get_response(ctx)
    if res is None:
        return None, None, None
    return res, res.status_code, res.headers


def raw_response(ctx):
    return _raw_response(ctx)


def json_response(ctx):
    res = get_response(ctx)
    if res is None:
        return None, None, None
    return res.json(), res.status_code, res.headers


def xmltodict_response(ctx):
    res = get_response(ctx)
    if res is None:
        return None, None, None
    return xmltodict.parse(res.text), res.status_code, res.headers


def html_response(ctx):
    res = get_response(ctx)
    if res is None:
        return None, None, None
    return html.fromstring(res.content), res.status_code, res.headers


def text_response(ctx):
    res = get_response(ctx)
    if res is None:
        return None, None, None
    return res.text, res.status_code, res.headers


class BaseRequestsSender(BaseSender, ABC):
    def __init__(self, middleware=None, base_uri=None, default_response_as=None):
        super().__init__(middleware, base_uri, default_response_as or _raw_response)

    def send(self, method, url, session_context=None, params=None, response_as=None, **kwargs):
        params = params or {}
        params = params if isinstance(params, Iterable) else params.to_dict()
        (url, params) = apply_params(url, params)
        request = FormationHttpRequest(
            url=urljoin(self.base_uri, url), method=method, params=params, **kwargs
        )
        return self.send_request(request, session_context, response_as)

    def send_request(self, request: FormationHttpRequest, session_context=None, response_as=None):
        ctx = {_REQ_HTTP: request}
        if session_context:
            ctx[_SESSION] = session_context
        ctx = wrap(self._get_adapter, middleware=self.middleware)(ctx)
        resolved_response_as = response_as or self.default_response_as
        return resolved_response_as(ctx)

    @abstractmethod
    def _get_adapter(self, ctx):
        pass


class Sender(BaseRequestsSender):
    def _get_adapter(self, ctx):
        return _requests_adapter(ctx, requests)


class SessionSender(BaseRequestsSender):
    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def _get_adapter(self, ctx):
        return _requests_adapter(ctx, self.session)


def _requests_adapter(ctx, requests_obj):
    req = ctx[_REQ_HTTP]
    method = getattr(requests_obj, req.method.lower())
    ctx[_RES_HTTP] = method(
        req.url,
        headers=req.headers,
        cookies=req.cookies,
        params=req.params,
        auth=req.auth,
        data=req.data,
        json=req.json,
        files=req.files,
        timeout=req.timeout,
        allow_redirects=req.allow_redirects,
    )
    return ctx
