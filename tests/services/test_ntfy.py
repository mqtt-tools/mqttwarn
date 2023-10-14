# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
import io
import re
from pathlib import Path

import pytest
import responses

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.services.ntfy import (
    ascii_clean,
    decode_jobitem,
    dict_ascii_clean,
    dict_with_titles,
    encode_rfc2047,
    obtain_ntfy_fields,
)
from mqttwarn.util import load_module_by_name


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


def test_ntfy_decode_jobitem_attachment_not_found_failure(caplog):
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

    assert (
        "ntfy: Attaching local file failed. Reason: [Errno 2] No such file or directory: '/tmp/mqttwarn-random-unknown'"
        in caplog.messages
    )


def test_ntfy_decode_jobitem_attachment_interpolate_name_failure(caplog):
    """
    Check how the `decode_jobitem` function fails when the template variables are invalid, or interpolation fails.
    """

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive", "file": "/tmp/mqttwarn-random-{foobar}"},
    )

    ntfy_request = decode_jobitem(item)

    assert ntfy_request.url == "http://localhost:9999/testdrive"
    assert ntfy_request.options["url"] == "http://localhost:9999/testdrive"
    assert ntfy_request.options["file"] == "/tmp/mqttwarn-random-{foobar}"
    assert "filename" not in ntfy_request.fields
    assert ntfy_request.attachment_data is None

    assert "ntfy: Computing attachment file name failed" in caplog.messages


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
def test_ntfy_plugin_attachment(srv, caplog, attachment_dummy):
    """
    Run a notification with an attachment.
    """

    responses.add(
        responses.PUT,
        "http://localhost:9999/testdrive",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.ntfy")

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive", "file": attachment_dummy.name},
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        data={
            "priority": "high",
            "tags": "foo,bar,äöü",
            "click": "https://example.org/testdrive",
            "actions": "view, Adjust temperature 🌡, https://example.org/home-automation/temperature, body='{{\"temperature\": 18}}'",  # noqa: E501
        },
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
    assert response.request.headers["Message"] == "=?utf-8?q?=E2=9A=BD_Notification_message_=E2=9A=BD?="
    assert response.request.headers["Tags"] == "=?utf-8?q?foo=2Cbar=2C=C3=A4=C3=B6=C3=BC?="
    assert (
        response.request.headers["Actions"]
        == "view, Adjust temperature ?, https://example.org/home-automation/temperature, body='{\"temperature\": 18}'"  # noqa: E501
    )

    assert response.response.status_code == 200

    assert "Successfully sent message using ntfy" in caplog.messages


@responses.activate
def test_ntfy_plugin_newline(srv, caplog, attachment_dummy):
    """
    Run a notification using newline characters.
    """

    responses.add(
        responses.POST,
        "http://localhost:9999/testdrive",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.ntfy")

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive"},
        title="⚽ Message title ⚽",
        message="Some\nmore\ntext...\n" + "⚽ Notification\nmessage ⚽" + "\nEven\nmore\ntext...",
        data={
            "priority": "high",
            "tags": "foo,bar,äöü",
            "click": "https://example.org/testdrive",
            "actions": "view, Adjust temperature 🌡, https://example.org/home-automation/temperature, body='{{\"temperature\": 18}}'",  # noqa: E501
        },
    )

    outcome = module.plugin(srv, item)

    assert "Successfully sent message using ntfy" in caplog.messages
    assert outcome is True

    assert len(responses.calls) == 1
    response = responses.calls[0]
    assert response.request.url == "http://localhost:9999/testdrive"
    assert isinstance(response.request.body, bytes)
    assert (
        response.request.body == b"Some\nmore\ntext...\n\xe2\x9a\xbd "
        b"Notification\nmessage \xe2\x9a\xbd\nEven\nmore\ntext..."
    )
    assert response.request.headers["User-Agent"] == "mqttwarn"
    assert "Message" not in response.request.headers
    assert response.request.headers["Tags"] == "=?utf-8?q?foo=2Cbar=2C=C3=A4=C3=B6=C3=BC?="
    assert (
        response.request.headers["Actions"]
        == "view, Adjust temperature ?, https://example.org/home-automation/temperature, body='{\"temperature\": 18}'"
    )

    assert response.response.status_code == 200

    assert "Successfully sent message using ntfy" in caplog.messages


@responses.activate
def test_ntfy_plugin_attachment_and_newline(srv, caplog, attachment_dummy):
    """
    Run a notification with an attachment, and newlines within the text message.
    """

    responses.add(
        responses.PUT,
        "http://localhost:9999/testdrive",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.ntfy")

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive", "file": attachment_dummy.name},
        title="⚽ Message title ⚽",
        message="Some\nmore\ntext...\n" + "⚽ Notification\nmessage ⚽" + "\nEven\nmore\ntext...",
        data={
            "priority": "high",
            "tags": "foo,bar,äöü",
            "click": "https://example.org/testdrive",
            "actions": "view, Adjust temperature 🌡, https://example.org/home-automation/temperature, body='{{\"temperature\": 18}}'",  # noqa: E501
        },
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
    assert (
        response.request.headers["Message"]
        == "=?utf-8?q?Some_more_text=2E=2E=2E_=E2=9A=BD_Notification_message_=E2=9A=BD_Even_more_text=2E=2E=2E?="
    )  # noqa: E501
    assert response.request.headers["Tags"] == "=?utf-8?q?foo=2Cbar=2C=C3=A4=C3=B6=C3=BC?="
    assert (
        response.request.headers["Actions"]
        == "view, Adjust temperature ?, https://example.org/home-automation/temperature, body='{\"temperature\": 18}'"  # noqa: E501
    )

    assert response.response.status_code == 200

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


@responses.activate
def test_ntfy_long_message(srv, caplog):
    """
    Test submitting messages longer than 76 characters.
    """

    responses.add(
        responses.POST,
        "http://localhost:9999/testdrive",
        json={"not": "relevant"},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.ntfy")

    item = Item(
        addrs={"url": "http://localhost:9999/testdrive"},
        title="Gerät angelernt",
        message="Das Gerät Kaffeevollautomat vom Typ Siemens TQ703D07 wurde angelernt",
    )

    outcome = module.plugin(srv, item)
    assert outcome is True
    assert "Successfully sent message using ntfy" in caplog.messages
    assert "requests.exceptions.InvalidHeader" not in caplog.text
