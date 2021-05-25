import pytest

from hs_formation.utils.attrs_serde import serde
from hs_formation.for_aio_http import (
    async_client,
    async_json_response,
    async_raw_response,
    async_xmltodict_response,
    async_text_response,
)
from hs_formation.middleware import (
    async_request_logger,
    async_ua,
    async_request_id,
    async_timeout,
    async_accept,
    async_request_duration,
)
from tests.utils import AsyncDummyLogger
from attr import attrib, attrs

@async_client
class HttpBin(object):
    base_uri = "https://httpbin.org"
    middleware = [
        async_request_id(key="x-flabber-id"),
        async_timeout(1.0),
        async_accept("application/json"),
        async_ua("the-fabricator/1.0.0"),
        async_request_logger(AsyncDummyLogger()),
    ]
    response_as = async_json_response

    async def get(self):
        return await self.request.get("get")

    async def post(self, data):
        return await self.request.post("post", data=data)

    async def put(self, data):
        return await self.request.put("put", data=data)

    async def delete(self):
        return await self.request.delete("delete")

    async def get_4xx(self):
        return await self.request.get("status/404")

    async def post_4xx(self, data):
        return await self.request.post("status/404", data=data)

    async def put_4xx(self, data):
        return await self.request.put("status/404", data=data)

    async def delete_4xx(self):
        return await self.request.delete("status/404")

    async def get_5xx(self):
        return await self.request.get("status/501")

    async def post_5xx(self, data):
        return await self.request.post("status/501", data=data)

    async def put_5xx(self, data):
        return await self.request.put("status/501", data=data)

    async def delete_5xx(self):
        return await self.request.delete("status/501")

    async def get_3xx(self):
        return await self.request.get("status/301")

    async def post_3xx(self, data):
        return await self.request.post("status/301", data=data)

    async def put_3xx(self, data):
        return await self.request.put("status/301", data=data)

    async def delete_3xx(self):
        return await self.request.delete("status/301")


@serde
@attrs
class Query(object):
    owner = attrib(metadata={"to": [":owner"]})
    repo = attrib(metadata={"to": [":repo"]})


@async_client
class Github(object):
    base_uri = "https://api.github.com/"
    middleware = []
    response_as = async_json_response

    async def stargazers(self, owner, repo):
        return await self.request.get(
            "repos/:owner/:repo/stargazers", params=Query(owner, repo)
        )


@async_client
class Openapi(object):
    base_uri = "http://api-hub-production-qa.omcomcom.com"
    middleware = [
        async_request_id(key="x-flabber-id"),
        async_timeout(1.0),
        async_accept("application/json"),
        async_ua("the-fabricator/1.0.0"),
        async_request_logger(AsyncDummyLogger()),
        async_request_duration(),
    ]
    response_as = async_json_response

    async def go(self, path="openapi.json"):
        return await self.request.get(path)


@async_client
class Google(object):
    base_uri = "https://www.google.com"
    response_as = async_text_response

    async def go(self, path="/"):
        return await self.request.get(path)


@async_client
class GoogleRaw(object):
    base_uri = "https://www.google.com/"
    response_as = async_raw_response

    async def go(self, path="/"):
        return await self.request.get(path)


@async_client
class XmlToDict(object):
    base_uri = "https://httpbin.org"
    response_as = async_xmltodict_response

    async def go(self, path="/xml"):
        return await self.request.get(path)


@async_client
class GoogleText(object):
    base_uri = "https://www.google.com/"
    response_as = async_text_response

    async def go(self, path="/"):
        return await self.request.get(path)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_json_all(snapshot):
    h = HttpBin()
    await h.get()
    try:
        await h.put_3xx({"testing": 123})
        pytest.fail("this method should not be allowed")
    except Exception as ex:
        pass

    try:
        await h.delete_3xx()
        pytest.fail("this method should not be allowed")
    except Exception as ex:
        pass

    try:
        await h.get_4xx()
        pytest.fail("404 empty response is not json")
    except Exception as ex:
        pass

    try:
        await h.post_4xx({"testing": 123})
        pytest.fail("404 empty response is not json")
    except Exception as ex:
        pass

    try:
        await h.put_4xx({"testing": 123})
        pytest.fail("404 empty response is not json")
    except Exception as ex:
        pass

    try:
        await h.delete_4xx({"testing": 123})
        pytest.fail("404 empty response is not json")
    except Exception as ex:
        pass

    try:
        await h.get_5xx()
        pytest.fail("5xx empty response is not json")
    except Exception as ex:
        pass

    try:
        await h.post_5xx({"testing": 123})
        pytest.fail("5xx empty response is not json")
    except Exception as ex:
        pass

    try:
        await h.put_5xx({"testing": 123})
        pytest.fail("5xx empty response is not json")
    except Exception as ex:
        pass

    try:
        await h.delete_5xx({"testing": 123})
        pytest.fail("5xx empty response is not json")
    except Exception as ex:
        pass


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_html_response(snapshot):
    google = Google()
    result = await google.go("/?q=formation")
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)

    # force error
    result = await google.go("/aint-no-body-here")
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_raw_response(snapshot):
    google = GoogleRaw()
    result = await google.go("/?q=formation")
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)

    # force error
    result = await google.go("/aint-no-body-here")
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_xmldict_response(snapshot):
    cl = XmlToDict()
    result = await cl.go()
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_text_response(snapshot):
    google = GoogleText()
    result = await google.go("/?q=formation")
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_json_response(snapshot):
    github = Github()
    result = await github.stargazers("jondot", "formation")
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)

    # force error
    result = await github.stargazers("no-body", "formation")
    snapshot.assert_match(result)
    snapshot.assert_match(result[0].parsed_content)
