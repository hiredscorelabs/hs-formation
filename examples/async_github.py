import asyncio

from hs_formation.for_aio_http import async_client, async_json_response
from hs_formation.middleware import async_request_logger
from hs_formation.utils.attrs_serde import serde
from attr import attrib, attrs

from tests.utils import AsyncDummyLogger


@serde
@attrs
class Query(object):
    owner = attrib(metadata={"to": [":owner"]})
    repo = attrib(metadata={"to": [":repo"]})


@async_client
class AsyncGithub(object):
    base_uri = "https://api.github.com/"
    middleware = [async_request_logger(AsyncDummyLogger())]
    response_as = async_json_response

    async def stargazers(self, owner, repo):
        return await self.request.get(
            "repos/:owner/:repo/stargazers", params=Query(owner, repo)
        )

    async def download(self, release):
        pass


async def main():
    github = AsyncGithub()
    (res, _, _) = await github.stargazers("jondot", "formation")
    print(res.parsed_content)


if __name__ == "__main__":
    asyncio.run(main())
