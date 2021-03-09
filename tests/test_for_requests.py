import pytest

from hs_formation.formation import apply_params
from hs_formation.for_requests import Sender
from hs_formation.middleware import ua, accept


def test_apply_params(snapshot):
    snapshot.assert_match(
        apply_params(
            "http://github.com/:user/:repo?q=foobar",
            {":user": "jondot", ":repo": "formation", "foobar": "foobaz"},
        )
    )


@pytest.mark.vcr()
def test_for_requests():
    sender = Sender(middleware=[])
    sender.get("http://example.com")


@pytest.mark.vcr()
def test_for_requests_with_params():
    sender = Sender(middleware=[])
    sender.get(
        "http://example.com",
        headers={"x-custom": "hello"},
        params={"v": "1.0"},
        data="some-data",
    )


@pytest.mark.vcr()
def test_ua():
    sender = Sender(middleware=[ua("foobar/1.0.0")])
    sender.get("http://example.com", headers={"x-custom": "hello"}, params={"v": "1.0"})
 

@pytest.mark.vcr()
def test_accept():
    sender = Sender(middleware=[accept("application/json")])
    sender.get("http://example.com", headers={"x-custom": "hello"}, params={"v": "1.0"})


@pytest.mark.vcr()
def test_cookies():
    sender = Sender(middleware=[])
    sender.get(
        "http://example.com",
        headers={"x-custom": "hello"},
        params={"v": "1.0"},
        cookies={"clientSession": "session"},
    )
