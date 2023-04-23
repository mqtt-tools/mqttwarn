# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
import io
import os
import re
import typing as t
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import responses

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.services.ntfy import (
    ascii_clean,
    decode_jobitem,
    dict_ascii_clean,
    dict_with_titles,
    encode_rfc2047,
    load_attachment,
    obtain_ntfy_fields,
)
from mqttwarn.util import load_module_by_name


@pytest.fixture
def attachment_dummy() -> t.Generator[t.IO[bytes], None, None]:
    """
    Provide a temporary files to the test cases to be used as an attachment with defined content.
    """
    tmp = NamedTemporaryFile(suffix=".txt", delete=False)
    tmp.write(b"foo")
    tmp.close()
    yield tmp
    os.unlink(tmp.name)


def test_ntfy_decode_jobitem_overview_success():
    """
    Test the `decode_jobitem` function with a few options.
    """

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive"},
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        data={"priority": "high", "tags": "foo,bar,äöü", "click": "https://example.org/testdrive"},
    )

    ntfy_request = decode_jobitem(item)

    assert ntfy_request.url == "http://localhost:9999/testdrive"
    assert ntfy_request.options["url"] == "http://localhost:9999/testdrive"
    assert ntfy_request.fields["message"] == "⚽ Notification message ⚽"
    assert ntfy_request.fields["title"] == "⚽ Message title ⚽"
    assert ntfy_request.fields["tags"] == "foo,bar,äöü"
    assert ntfy_request.fields["priority"] == "high"
    assert ntfy_request.fields["click"] == "https://example.org/testdrive"


def test_ntfy_decode_jobitem_attachment_success(attachment_dummy):
    """
    Test the `decode_jobitem` function with an attachment.
    """

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive", "file": attachment_dummy.name},
    )

    ntfy_request = decode_jobitem(item)

    assert ntfy_request.url == "http://localhost:9999/testdrive"
    assert ntfy_request.options["url"] == "http://localhost:9999/testdrive"
    assert ntfy_request.options["file"] == attachment_dummy.name
    assert ntfy_request.fields["filename"] == Path(attachment_dummy.name).name
    assert ntfy_request.attachment_data.read() == b"foo"


def test_ntfy_decode_jobitem_attachment_failure(caplog):
    """
    Test the `decode_jobitem` function with an invalid attachment.
    """

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive", "file": "/tmp/mqttwarn-random-unknown"},
    )

    ntfy_request = decode_jobitem(item)

    assert ntfy_request.url == "http://localhost:9999/testdrive"
    assert ntfy_request.options["url"] == "http://localhost:9999/testdrive"
    assert ntfy_request.options["file"] == "/tmp/mqttwarn-random-unknown"
    assert "filename" not in ntfy_request.fields
    assert ntfy_request.attachment_data is None

    assert "ntfy: Accessing attachment file failed: /tmp/mqttwarn-random-unknown" in caplog.messages


def test_ntfy_decode_jobitem_attachment_with_filename_success(attachment_dummy):
    """
    Test the `decode_jobitem` function with a user-provided `filename` field.
    """

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive", "file": attachment_dummy.name},
        data={"filename": "testdrive.txt"},
    )

    ntfy_request = decode_jobitem(item)

    assert ntfy_request.url == "http://localhost:9999/testdrive"
    assert ntfy_request.options["url"] == "http://localhost:9999/testdrive"
    assert ntfy_request.options["file"] == attachment_dummy.name
    assert ntfy_request.fields["filename"] == "testdrive.txt"
    assert ntfy_request.attachment_data.read() == b"foo"


def test_ntfy_decode_jobitem_with_url_only_success():
    """
    Test the `decode_jobitem` function when `addrs` is an URL only.
    """

    item = Item(addrs="http://localhost:9999/testdrive")

    ntfy_request = decode_jobitem(item)

    assert ntfy_request.url == "http://localhost:9999/testdrive"
    assert ntfy_request.options["url"] == "http://localhost:9999/testdrive"


def test_ntfy_decode_jobitem_with_invalid_target_address_descriptor():
    """
    Test the `decode_jobitem` function when `addrs` is of an invalid type.
    """

    item = Item(addrs=None)
    with pytest.raises(TypeError) as ex:
        decode_jobitem(item)
    assert ex.match(re.escape("Unable to handle `targets` address descriptor data type `NoneType`: None"))

    item = Item(addrs=42.42)
    with pytest.raises(TypeError) as ex:
        decode_jobitem(item)
    assert ex.match(re.escape("Unable to handle `targets` address descriptor data type `float`: 42.42"))


def test_ntfy_obtain_ntfy_fields_from_transformation_data():
    """
    Test the `obtain_ntfy_fields` function with transformation data.

    Verify it does not emit fields unknown to ntfy. Here: `garbage`.
    """
    indata = {"message": "⚽ Notification message ⚽", "priority": "high", "garbage": "foobar"}
    item = Item(data=indata)
    outdata = obtain_ntfy_fields(item)
    assert list(outdata.keys()) == ["message", "priority"]


def test_ntfy_obtain_ntfy_fields_from_config():
    """
    Verify `obtain_ntfy_fields` also obtains data from the configuration section.
    """
    indata = {"message": "⚽ Notification message ⚽", "priority": "high", "garbage": "foobar"}
    item = Item(config=indata)
    outdata = obtain_ntfy_fields(item)
    assert list(outdata.keys()) == ["message", "priority"]


def test_ntfy_obtain_ntfy_fields_from_options():
    """
    Verify `obtain_ntfy_fields` also obtains data from the target options (addrs).
    """
    indata = {"message": "⚽ Notification message ⚽", "priority": "high", "garbage": "foobar"}
    item = Item(addrs=indata)
    outdata = obtain_ntfy_fields(item)
    assert list(outdata.keys()) == ["message", "priority"]


def test_ntfy_obtain_ntfy_fields_precedence():
    """
    Verify precedence handling of `obtain_ntfy_fields` when obtaining the same fields from multiple sources.
    """
    item = Item(config={"message": "msg-config"}, addrs={"message": "msg-addrs"}, data={"message": "msg-data"})
    outdata = obtain_ntfy_fields(item)
    assert outdata["message"] == "msg-data"

    item = Item(config={"message": "msg-config"}, addrs={"message": "msg-addrs"})
    outdata = obtain_ntfy_fields(item)
    assert outdata["message"] == "msg-addrs"

    item = Item(config={"message": "msg-config"})
    outdata = obtain_ntfy_fields(item)
    assert outdata["message"] == "msg-config"


def test_ntfy_load_attachment_tplvar_failure(caplog):
    """
    Check how the `load_attachment` helper function fails when the template variables are invalid.
    """
    path, data = load_attachment(None, None)

    assert path is None
    assert data is None

    assert "ntfy: Computing attachment file name failed" in caplog.messages
    assert "AttributeError: 'NoneType' object has no attribute 'format'" in caplog.text


def test_ntfy_dict_with_titles():
    """
    Test the `dict_with_titles` helper function.
    """
    indata = {"foo": "bar"}
    outdata = {"Foo": "bar"}
    assert dict_with_titles(indata) == outdata


def test_ntfy_dict_ascii_clean():
    """
    Test the `dict_ascii_clean` helper function.
    """
    indata = {"message": "⚽ Notification message ⚽", "foobar": "äöü"}
    outdata = dict_ascii_clean(indata)
    assert outdata["message"] == "? Notification message ?"
    assert outdata["foobar"] == "???"


def test_ntfy_ascii_clean_success():
    """
    Test the `ascii_clean` helper function.
    """
    assert ascii_clean("⚽ Notification message ⚽") == "? Notification message ?"
    assert ascii_clean("⚽ Notification message ⚽".encode("utf-8")) == "? Notification message ?"


def test_ntfy_encode_rfc2047():
    """
    Test the `ascii_clean` helper function.
    """
    message_in = "⚽ Notification message ⚽"
    message_out = "=?utf-8?q?=E2=9A=BD_Notification_message_=E2=9A=BD?="
    assert encode_rfc2047(message_in) == message_out
    assert encode_rfc2047(message_in.encode("utf-8")) == message_out


def test_ntfy_ascii_clean_failure():
    """
    Test the `ascii_clean` helper function.
    """
    with pytest.raises(TypeError) as ex:
        ascii_clean(None)
    assert ex.match(re.escape("Unknown data type to compute ASCII-clean variant: NoneType"))


@responses.activate
def test_ntfy_plugin_success(srv, caplog, attachment_dummy):
    """
    Test the whole plugin with a successful outcome.
    """

    ntfy_api_response = {
        "id": "jBXrDQF4e8ab",
        "time": 1681939903,
        "expires": 1681983103,
        "event": "message",
        "topic": "frigate-test",
        "title": "goat entered lawn at 2023-04-06 14:31:46.638857+00:00",
        "message": "goat was in barn before",
        "click": "https://frigate.local/events?camera=cam-testdrive\\u0026label=goat\\u0026zone=lawn",
        "attachment": {
            "name": "mqttwarn-frigate-cam-testdrive-goat.png",
            "type": "image/png",
            "size": 283595,
            "expires": 1681950703,
            "url": "http://localhost:5555/file/jBXrDQF4e8ab.png",
        },
    }

    responses.add(
        responses.PUT,
        "http://localhost:9999/testdrive",
        json=ntfy_api_response,
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.ntfy")

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive", "file": attachment_dummy.name},
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        data={"priority": "high", "tags": "foo,bar,äöü", "click": "https://example.org/testdrive"},
    )

    outcome = module.plugin(srv, item)

    assert "Successfully sent message using ntfy" in caplog.messages
    assert outcome is True

    assert len(responses.calls) == 1
    response = responses.calls[0]
    assert response.request.url == "http://localhost:9999/testdrive"
    assert isinstance(response.request.body, io.BufferedReader)
    assert response.request.body.read() == b"foo"
    assert response.request.headers["User-Agent"] == "mqttwarn"
    assert response.request.headers["Tags"] == "=?utf-8?q?foo=2Cbar=2C=C3=A4=C3=B6=C3=BC?="

    assert response.response.status_code == 200
    assert response.response.json() == ntfy_api_response

    assert "Successfully sent message using ntfy" in caplog.messages


def test_ntfy_plugin_api_failure(srv, caplog):
    """
    Processing a message without an ntfy backend API should fail.
    """

    module = load_module_by_name("mqttwarn.services.ntfy")

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive"},
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
    )

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Request to ntfy API failed" in caplog.messages
