import structlog

from hs_formation.for_requests import client, json_response
from hs_formation.middleware import request_logger


@client
class HttpBin:
    base_uri = "https://httpbin.org"
    response_as = json_response
    middleware = [
        request_logger(structlog.getLogger()),
    ]


if __name__ == "__main__":
    httpbin = HttpBin()
    with httpbin.session() as s:
        s.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
        r = s.get('https://httpbin.org/cookies')
        print(r[0]['cookies'])
