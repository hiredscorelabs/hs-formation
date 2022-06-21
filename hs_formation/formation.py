import datetime
from abc import abstractmethod, ABC
from typing import Type
from toolz import reduce
from toolz.curried import keyfilter, reduce
from urllib.parse import urljoin
from attr import attrib, attrs
from functools import partial

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


class BaseSender(ABC):
    def __init__(self, middleware, base_uri, default_response_as):
        self.middleware = middleware
        self.base_uri = base_uri
        self.default_response_as = default_response_as

    def get(self, path, **kwargs):
        return self.send("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self.send("post", path, **kwargs)

    def put(self, path, **kwargs):
        return self.send("put", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.send("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.send("delete", path, **kwargs)

    @abstractmethod
    def send(self, method, url, session_context=None, params=None, response_as=None, **kwargs):
        pass


def client_decorator(cls, sender_class: Type[BaseSender], session_class: Type[BaseSender] = None):
    original_init = cls.__init__

    def now_iso(self):
        return datetime.datetime.utcnow().isoformat()

    def path(self, p):
        return urljoin(self.base_uri, p)

    def init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.base_uri = kwargs.get(
            "base_uri", getattr(self.__class__, "base_uri", "http://localhost")
        )
        response_as = kwargs.get(
            "response_as", getattr(self.__class__, "response_as", None)
        )
        middleware = kwargs.get(
            "middleware", getattr(self.__class__, "middleware", [])
        ) or []
        self.request = sender_class(
            middleware=middleware, base_uri=self.base_uri, default_response_as=response_as
        )
        if session_class:
            self.session = partial(session_class,
                middleware=middleware, base_uri=self.base_uri, default_response_as=response_as
            )

    cls.path = path
    cls.now_iso = now_iso
    cls.__init__ = init
    return cls


@attrs
class FormationHttpRequest:
    url = attrib()
    method = attrib(default="get")

    # these two are very stabby. a single default instance is shared among all attrs
    # objects. to assign new keys, update immutably -- use merge and re-assign
    headers = attrib(factory=dict)
    cookies = attrib(factory=dict)
    params = attrib(factory=dict)

    auth = attrib(default=None)
    data = attrib(default=None)
    json = attrib(default=None)
    files = attrib(default=None)
    timeout = attrib(default=None)
    allow_redirects = attrib(default=True)


def wrap(call, middleware=None):
    if middleware is None:
        middleware = []
    return reduce(
        lambda acc, m: lambda ctx: m(ctx, acc),
        reversed(middleware),
        lambda ctx: call(ctx),
    )


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
