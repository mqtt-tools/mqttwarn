# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
"""
This file contains test cases for the v1 configuration layout variant,
where `addrs` is a list.
"""
import dataclasses
import re
import typing as t
from operator import attrgetter

import pytest

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file
from tests.services.pushsafer.util import TEST_TOKEN, assert_request, get_reference_data


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
class IoTestItem:
    id: str  # noqa: A003
    in_addrs: t.List[str]
    out_data: t.Dict[str, str]


variants = [
    IoTestItem(id="device-id", in_addrs=[TEST_TOKEN, "52|65|78"], out_data={"d": "52|65|78"}),
    IoTestItem(id="icon", in_addrs=[TEST_TOKEN, "", "test.ico"], out_data={"i": "test.ico"}),
    IoTestItem(id="sound", in_addrs=[TEST_TOKEN, "", "", "test.mp3"], out_data={"s": "test.mp3"}),
    IoTestItem(id="vibration", in_addrs=[TEST_TOKEN, "", "", "", "2"], out_data={"v": "2"}),
    IoTestItem(
        id="url", in_addrs=[TEST_TOKEN, "", "", "", "", "http://example.org"], out_data={"u": "http://example.org"}
    ),
    IoTestItem(
        id="url-title", in_addrs=[TEST_TOKEN, "", "", "", "", "", "Example Org"], out_data={"ut": "Example Org"}
    ),
    IoTestItem(id="time-to-live", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "60"], out_data={"l": "60"}),
    IoTestItem(id="priority", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "2"], out_data={"pr": "2"}),
    IoTestItem(id="retry", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "60"], out_data={"re": "60"}),
    IoTestItem(id="expire", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "", "600"], out_data={"ex": "600"}),
    IoTestItem(id="answer", in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "", "", "0"], out_data={"a": "0"}),
    IoTestItem(
        id="answer-options",
        in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "", "", "1", "yes|no"],
        out_data={"a": "1", "ao": "yes|no"},
    ),
    IoTestItem(
        id="answer-force",
        in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "", "", "1", "", "1"],
        out_data={"a": "1", "af": "1"},
    ),
    IoTestItem(
        id="confirm-repeat",
        in_addrs=[TEST_TOKEN, "", "", "", "", "", "", "", "", "", "", "1", "", "", "45"],
        out_data={"a": "1", "cr": "45"},
    ),
]


@pytest.mark.parametrize("variant", variants, ids=attrgetter("id"))
def test_pushsafer_variant(srv, caplog, mock_urlopen_success, variant: IoTestItem):
    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=variant.in_addrs, message="⚽ Notification message ⚽")
    outcome = module.plugin(srv, item)

    request = mock_urlopen_success.call_args[0][0]
    assert_request(request, get_reference_data(**variant.out_data))

    assert outcome is True
    assert "Sending pushsafer notification" in caplog.text
    assert "Successfully sent pushsafer notification" in caplog.text
