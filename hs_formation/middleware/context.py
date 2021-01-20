from ..formation import _CONTEXT, _REQ_ID, _REQ_PARENT_ID, _SESSION, _UID
import os
from six.moves import _thread as thread
from toolz.curried import get_in


def get_context(
    request_id=None,
    request_parent_id=None,
    namespace="service",
    env="local",
    sha="dev",
    version="0.0.1",
    scope="service",
    uid=None,
    getpid=os.getpid,
    gettid=thread.get_ident,
):
    pid = getpid()
    tid = gettid()
    return {
        "v": version,
        "sha": sha,
        "env": env,
        "pid": pid,
        "tid": tid,
        "uid": uid,
        "scope": scope,
        "ns": namespace,
        "rid": request_id,
        "rid_p": request_parent_id,
    }


def call_context_fnc(ctx, context_fn, namespace, scope, env, sha, version, getpid, gettid):
    request_id = ctx.get(_REQ_ID, None)
    request_parent_id = ctx.get(_REQ_PARENT_ID, None)
    uid = get_in([_SESSION, _UID], None)

    ctx[_CONTEXT] = context_fn(
        env=env,
        sha=sha,
        namespace=namespace,
        version=version,
        request_id=request_id,
        request_parent_id=request_parent_id,
        scope=scope,
        uid=uid,
        getpid=getpid,
        gettid=gettid,
    )
    return ctx


def context(
    context_fn=get_context,
    namespace="service",
    scope="all",
    env="local",
    sha="dev",
    version="0.01",
    getpid=os.getpid,
    gettid=thread.get_ident,
):
    def context_middleware(ctx, call):
        ctx = call_context_fnc(
            ctx, context_fn, namespace, scope, env, sha, version, getpid, gettid
        )
        ctx = call(ctx)
        return ctx

    return context_middleware


def async_context(
    context_fn=get_context,
    namespace="service",
    scope="all",
    env="local",
    sha="dev",
    version="0.01",
    getpid=os.getpid,
    gettid=thread.get_ident,
):
    async def context_middleware(ctx, call):
        ctx = call_context_fnc(
            ctx, context_fn, namespace, scope, env, sha, version, getpid, gettid
        )
        ctx = await call(ctx)
        return ctx

    return context_middleware
