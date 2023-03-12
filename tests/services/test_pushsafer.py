# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
import dataclasses
import re
import typing as t
import urllib.request
from operator import attrgetter
from urllib.parse import parse_qsl

import pytest

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file
from tests.util import FakeResponse

TEST_TOKEN = "myToken"


def get_reference_data(**more_data):
    data = {
        "m": "⚽ Notification message ⚽",
        "k": "myToken",
        "expire": "3600",
    }
    data.update(more_data)
    return data


def assert_request(request: urllib.request.Request, data: t.Dict[str, str]):
    assert request.full_url == "https://www.pushsafer.com/api"
    assert dict(parse_qsl(request.data.decode("utf-8"))) == data


@pytest.fixture
def mock_urlopen_success(mocker):
    return mocker.patch("urllib.request.urlopen", return_value=FakeResponse(data=b'{"status": 1}'))


@pytest.fixture
def mock_urlopen_failure(mocker):
    return mocker.patch("urllib.request.urlopen", return_value=FakeResponse(data=b'{"status": 6}'))


def test_pushsafer_parameter_failure(srv, caplog, mock_urlopen_success):
    """
    Test Pushsafer service with zero `addrs` parameters. It should fail.
    """

    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=[], message="⚽ Notification message ⚽")
    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Pushsafer private or alias key not configured. target=None" in caplog.messages


def test_pushsafer_basic_success(srv, caplog, mock_urlopen_success):
    """
    Test Pushsafer service with only a single `addrs` parameter, the authentication key/token.
    """

    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=[TEST_TOKEN], message="⚽ Notification message ⚽")
    outcome = module.plugin(srv, item)

    request = mock_urlopen_success.call_args[0][0]
    assert_request(request, get_reference_data())

    assert outcome is True
    assert "Sending pushsafer notification" in caplog.text
    assert "Successfully sent pushsafer notification" in caplog.text


def test_pushsafer_title_success(srv, caplog, mock_urlopen_success):
    """
    Test Pushsafer service with title.
    """

    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=[TEST_TOKEN], message="⚽ Notification message ⚽", title="⚽ Message title ⚽")
    outcome = module.plugin(srv, item)

    request = mock_urlopen_success.call_args[0][0]
    assert_request(request, get_reference_data(t="⚽ Message title ⚽"))

    assert outcome is True
    assert "Sending pushsafer notification" in caplog.text
    assert "Successfully sent pushsafer notification" in caplog.text


def test_pushsafer_basic_failure(srv, caplog, mock_urlopen_failure):
    """
    Test Pushsafer service with a response indicating an error.
    """

    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=[TEST_TOKEN], message="⚽ Notification message ⚽")
    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Sending pushsafer notification" in caplog.text
    assert re.match('.*Error sending pushsafer notification.*{"status": 6}.*', caplog.text, re.DOTALL)


def test_pushsafer_token_environment_success(srv, caplog, mocker, mock_urlopen_success):
    """
    Test Pushsafer service with token from `PUSHSAFER_TOKEN` environment variable.
    """
    mocker.patch.dict("os.environ", {"PUSHSAFER_TOKEN": TEST_TOKEN})

    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=[""], message="⚽ Notification message ⚽")
    outcome = module.plugin(srv, item)

    request = mock_urlopen_success.call_args[0][0]
    assert_request(request, get_reference_data())

    assert outcome is True
    assert "Sending pushsafer notification" in caplog.text
    assert "Successfully sent pushsafer notification" in caplog.text


@dataclasses.dataclass
class TestItem:
    id: str  # noqa: A003
    in_addrs: t.List[str]
    out_data: t.Dict[str, str]


variants = [
    TestItem(id="device-id", in_addrs=[TEST_TOKEN, "52|65|78"], out_data={"d": "52|65|78"}),
    TestItem(id="icon", in_addrs=[TEST_TOKEN, "", "test.ico"], out_data={"i": "test.ico"}),
    TestItem(id="sound", in_addrs=[TEST_TOKEN, "", "", "test.mp3"], out_data={"s": "test.mp3"}),
    TestItem(id="vibration", in_addrs=[TEST_TOKEN, "", "", "", "true"], out_data={"v": "true"}),
    TestItem(
        id="url", in_addrs=[TEST_TOKEN, "", "", "", "", "http://example.org"], out_data={"u": "http://example.org"}
    ),
    TestItem(id="url-title", in_addrs=[TEST_TOKEN, "", "", "", "", "", "Example Org"], out_data={"ut": "Example Org"}),
    TestItem(id="time-to-live", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "60"], out_data={"l": "60"}),
    TestItem(id="priority", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "2"], out_data={"pr": "2"}),
    TestItem(id="retry", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "60"], out_data={"re": "60"}),
    TestItem(id="expire", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "", "600"], out_data={"ex": "600"}),
    TestItem(id="answer", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "", "", "0"], out_data={"a": "0"}),
]


@pytest.mark.parametrize("variant", variants, ids=attrgetter("id"))
def test_pushsafer_variant(srv, caplog, mock_urlopen_success, variant: TestItem):
    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=variant.in_addrs, message="⚽ Notification message ⚽")
    outcome = module.plugin(srv, item)

    request = mock_urlopen_success.call_args[0][0]
    assert_request(request, get_reference_data(**variant.out_data))

    assert outcome is True
    assert "Sending pushsafer notification" in caplog.text
    assert "Successfully sent pushsafer notification" in caplog.text
