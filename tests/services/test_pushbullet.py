# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
import pytest
import responses

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_by_name

# Canonical API response used for all tests.
pushbullet_api_response = {
    "active": True,
    "body": "⚽ Notification message ⚽",
    "created": 1412047948.579029,
    "direction": "self",
    "dismissed": False,
    "iden": "ujpah72o0sjAoRtnM0jc",
    "modified": 1412047948.579031,
    "receiver_email": "test@example.org",
    "receiver_email_normalized": "test@example.org",
    "receiver_iden": "ujpah72o0",
    "sender_email": "sender@example.org",
    "sender_email_normalized": "sender@example.org",
    "sender_iden": "ujpah72o0",
    "sender_name": "Maxine Musterfrau",
    "title": "⚽ Message title ⚽",
    "type": "note",
}


@responses.activate
def test_pushbullet_modern_email_success(srv, caplog):
    """
    Test the whole plugin with a successful outcome, using the modern configuration variant.

    https://docs.pushbullet.com/#push
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json=pushbullet_api_response,
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs={
            "access_token": "a6FJVAA0LVJKrT8k",
            "recipient": "test@example.org",
            "recipient_type": "email",
        },
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    outcome = module.plugin(srv, item)

    assert "Sending Pushbullet notification to foo" in caplog.messages
    assert "Successfully sent Pushbullet notification" in caplog.messages
    assert outcome is True

    assert len(responses.calls) == 1
    response = responses.calls[0]
    assert response.request.url == "https://api.pushbullet.com/v2/pushes"
    assert isinstance(response.request.body, bytes)
    assert response.request.headers["User-Agent"] == "mqttwarn"
    assert response.request.headers["Access-Token"] == "a6FJVAA0LVJKrT8k"

    assert response.response.status_code == 200
    assert response.response.json() == pushbullet_api_response


@responses.activate
def test_pushbullet_modern_device_success(srv, caplog):
    """
    Test the whole plugin with a successful outcome, using the modern configuration variant.

    https://docs.pushbullet.com/#push
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json=pushbullet_api_response,
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs={
            "access_token": "a6FJVAA0LVJKrT8k",
            "recipient": "ujpah72o0sjAoRtnM0jc",
        },
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    outcome = module.plugin(srv, item)

    assert "Sending Pushbullet notification to foo" in caplog.messages
    assert "Successfully sent Pushbullet notification" in caplog.messages
    assert outcome is True


@responses.activate
@pytest.mark.parametrize("recipient_type", [None, "channel", "client"])
def test_pushbullet_modern_recipient_types_success(srv, caplog, recipient_type):
    """
    Verify using all available recipient types works.
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs={
            "access_token": "a6FJVAA0LVJKrT8k",
            "recipient": "ujpah72o0sjAoRtnM0jc",
            "recipient_type": recipient_type,
        },
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    outcome = module.plugin(srv, item)

    assert "Sending Pushbullet notification to foo" in caplog.messages
    assert "Successfully sent Pushbullet notification" in caplog.messages
    assert outcome is True


@responses.activate
@pytest.mark.parametrize("recipient_type", ["unknown"])
def test_pushbullet_modern_recipient_type_failure(srv, caplog, recipient_type):
    """
    Verify using an unknown recipient type fails.
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs={
            "access_token": "a6FJVAA0LVJKrT8k",
            "recipient": "ujpah72o0sjAoRtnM0jc",
            "recipient_type": recipient_type,
        },
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    outcome = module.plugin(srv, item)

    assert "Sending Pushbullet notification to foo" in caplog.messages
    assert "Sending Pushbullet notification failed" in caplog.messages
    assert outcome is False


@responses.activate
def test_pushbullet_legacy_device_success(srv, caplog):
    """
    Test the whole plugin with a successful outcome, using the legacy configuration variant.

    https://docs.pushbullet.com/#push
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs=["a6FJVAA0LVJKrT8k", "ujpah72o0sjAoRtnM0jc"],
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    outcome = module.plugin(srv, item)

    assert "Sending Pushbullet notification to foo" in caplog.messages
    assert "Successfully sent Pushbullet notification" in caplog.messages
    assert outcome is True


@responses.activate
def test_pushbullet_legacy_email_success(srv, caplog):
    """
    Test the whole plugin with a successful outcome, using the legacy configuration variant.

    https://docs.pushbullet.com/#push
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs=["a6FJVAA0LVJKrT8k", "test@example.org", "email"],
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    outcome = module.plugin(srv, item)

    assert "Sending Pushbullet notification to foo" in caplog.messages
    assert "Successfully sent Pushbullet notification" in caplog.messages
    assert outcome is True


@responses.activate
def test_pushbullet_legacy_failure(srv, caplog):
    """
    Test the whole plugin with a failure outcome, using the legacy configuration variant.

    https://docs.pushbullet.com/#push
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs=["a6FJVAA0LVJKrT8k"],
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    with pytest.raises(ValueError) as ex:
        module.plugin(srv, item)
    assert ex.match("Pushbullet target is incorrectly configured")


@responses.activate
def test_pushbullet_tad_wrong_type_failure(srv, caplog):
    """
    Test failure conditions of plugin.
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs=42.42,
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    with pytest.raises(ValueError) as ex:
        module.plugin(srv, item)
    assert ex.match("Unknown target address descriptor type: float")


@responses.activate
def test_pushbullet_api_failure(srv, caplog, mocker):
    """
    Test failure conditions of plugin.
    """

    responses.add(
        responses.POST,
        "https://api.pushbullet.com/v2/pushes",
        json={},
        status=200,
    )

    module = load_module_by_name("mqttwarn.services.pushbullet")

    item = Item(
        addrs={
            "access_token": "a6FJVAA0LVJKrT8k",
            "recipient": "ujpah72o0sjAoRtnM0jc",
        },
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        target="foo",
    )

    def raise_exception(*args, **kwargs):
        raise Exception("Something failed")

    module.send_note = raise_exception

    outcome = module.plugin(srv, item)
    assert outcome is False

    assert "Sending Pushbullet notification failed" in caplog.messages
    assert "Something failed" in caplog.text
