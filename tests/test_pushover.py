import base64
import logging
import os
from unittest import mock

import responses
from requests_toolbelt import MultipartDecoder

from mqttwarn.util import load_module_from_file
from tests.util import ProcessorItem as Item


def add_successful_mock_response():
    responses.add(
        responses.POST,
        "https://api.pushover.net/1/messages.json",
        json={"status": 1},
        status=200,
    )


def add_failed_mock_response():
    responses.add(
        responses.POST,
        "https://api.pushover.net/1/messages.json",
        json={"status": 999},
        status=400,
    )


@responses.activate
def test_pushover_success(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2"],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()
        outcome = module.plugin(srv, item)

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url == "https://api.pushover.net/1/messages.json"
        )
        assert (
            responses.calls[0].request.body
            == "user=userkey2&token=appkey2&retry=60&expire=3600&message=%E2%9A%BD+Notification+message+%E2%9A%BD"
        )
        assert responses.calls[0].request.headers["User-Agent"] == "mqttwarn"

        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.text == '{"status": 1}'

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
@mock.patch.dict(os.environ, {"PUSHOVER_USER": "userkey2", "PUSHOVER_TOKEN": "appkey2"})
def test_pushover_success_with_credentials_from_environment(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=[None, None],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()
        outcome = module.plugin(srv, item)

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url == "https://api.pushover.net/1/messages.json"
        )
        assert (
            responses.calls[0].request.body
            == "user=userkey2&token=appkey2&retry=60&expire=3600&message=%E2%9A%BD+Notification+message+%E2%9A%BD"
        )
        assert responses.calls[0].request.headers["User-Agent"] == "mqttwarn"

        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.text == '{"status": 1}'

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
def test_pushover_success_with_sound(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2", "sound1"],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()
        outcome = module.plugin(srv, item)

        assert (
            responses.calls[0].request.body
            == "user=userkey2&token=appkey2&retry=60&expire=3600&sound=sound1&message=%E2%9A%BD+Notification+message+%E2%9A%BD"
        )

        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.text == '{"status": 1}'

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
def test_pushover_success_with_devices(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2", None, "cellphone1,cellphone2"],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()
        outcome = module.plugin(srv, item)

        assert (
            responses.calls[0].request.body
            == "user=userkey2&token=appkey2&retry=60&expire=3600&devices=cellphone1%2Ccellphone2&message=%E2%9A%BD+Notification+message+%E2%9A%BD"
        )

        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.text == '{"status": 1}'

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
def test_pushover_success_with_callback_and_title_and_priority_and_alternative_message(
    srv, caplog
):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={"callback": "https://example.org/pushover-callback"},
        target="test",
        addrs=["userkey2", "appkey2"],
        priority=555,
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        data={"message": "⚽ Alternative notification message ⚽"},
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()
        outcome = module.plugin(srv, item)

        assert (
            responses.calls[0].request.body
            == "user=userkey2&token=appkey2&retry=60&expire=3600&title=%E2%9A%BD+Message+title+%E2%9A%BD&priority=555&callback=https%3A%2F%2Fexample.org%2Fpushover-callback&message=%E2%9A%BD+Alternative+notification+message+%E2%9A%BD"
        )

        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.text == '{"status": 1}'

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
def test_pushover_success_with_imageurl(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2"],
        message="⚽ Notification message ⚽",
        data={"imageurl": "https://example.org/image"},
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()

        image = open("./assets/pushover.png", "rb").read()
        responses.add(
            responses.GET,
            "https://example.org/image",
            body=image,
            stream=True,
            status=200,
        )

        outcome = module.plugin(srv, item)

        # Check response status.
        assert responses.calls[1].response.status_code == 200
        assert responses.calls[1].response.text == '{"status": 1}'

        # Decode multipart request.
        request = responses.calls[1].request
        decoder = MultipartDecoder(request.body, request.headers["Content-Type"])

        content_disposition_headers = []
        contents = {}
        for part in decoder.parts:
            content_disposition_headers.append(part.headers[b"Content-Disposition"])

            key = part.headers[b"Content-Disposition"]
            contents[key] = part.content

        # Proof request has all body parts.
        assert content_disposition_headers == [
            b'form-data; name="user"',
            b'form-data; name="token"',
            b'form-data; name="retry"',
            b'form-data; name="expire"',
            b'form-data; name="message"',
            b'form-data; name="attachment"; filename="image.jpg"',
        ]

        # Proof parameter body parts, modulo image content, have correct values.
        assert list(contents.values())[:-1] == [
            b"userkey2",
            b"appkey2",
            b"60",
            b"3600",
            b"\xe2\x9a\xbd Notification message \xe2\x9a\xbd",
        ]

        # Proof image has content.
        assert len(decoder.parts[-1].content) == 45628

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
def test_pushover_success_with_imageurl_and_basic_authentication(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2"],
        message="⚽ Notification message ⚽",
        data={
            "imageurl": "https://example.org/image",
            "auth": "basic",
            "user": "foo",
            "password": "bar",
        },
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()

        image = open("./assets/pushover.png", "rb").read()
        responses.add(
            responses.GET,
            "https://example.org/image",
            body=image,
            stream=True,
            status=200,
        )

        outcome = module.plugin(srv, item)

        # Proof authentication on image request.
        assert (
            responses.calls[0].request.headers["Authorization"] == "Basic Zm9vOmJhcg=="
        )

        # Check response status.
        assert responses.calls[1].response.status_code == 200
        assert responses.calls[1].response.text == '{"status": 1}'

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
def test_pushover_success_with_imageurl_and_digest_authentication(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2"],
        message="⚽ Notification message ⚽",
        data={
            "imageurl": "https://example.org/image",
            "auth": "digest",
            "user": "foo",
            "password": "bar",
        },
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()

        image = open("./assets/pushover.png", "rb").read()
        responses.add(
            responses.GET,
            "https://example.org/image",
            body=image,
            stream=True,
            status=200,
        )

        outcome = module.plugin(srv, item)

        # Proof authentication on image request.
        # FIXME: Currently not possible because Digest auth will only work if
        #        the server answers with 4xx.
        # assert (
        #    responses.calls[0].request.headers["Authorization"] == "Digest something"
        # )

        # Check response status.
        assert responses.calls[1].response.status_code == 200
        assert responses.calls[1].response.text == '{"status": 1}'

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


@responses.activate
def test_pushover_success_with_imagebase64(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    image = open("./assets/pushover.png", "rb").read()
    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2"],
        message="⚽ Notification message ⚽",
        data={"imagebase64": base64.encodebytes(image)},
    )

    with caplog.at_level(logging.DEBUG):

        add_successful_mock_response()
        outcome = module.plugin(srv, item)

        # Check response status.
        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.text == '{"status": 1}'

        # Decode multipart request.
        request = responses.calls[0].request
        decoder = MultipartDecoder(request.body, request.headers["Content-Type"])

        content_disposition_headers = []
        contents = {}
        for part in decoder.parts:
            content_disposition_headers.append(part.headers[b"Content-Disposition"])

            key = part.headers[b"Content-Disposition"]
            contents[key] = part.content

        # Proof request has all body parts.
        assert content_disposition_headers == [
            b'form-data; name="user"',
            b'form-data; name="token"',
            b'form-data; name="retry"',
            b'form-data; name="expire"',
            b'form-data; name="message"',
            b'form-data; name="attachment"; filename="image.jpg"',
        ]

        # Proof parameter body parts, modulo image content, have correct values.
        assert list(contents.values())[:-1] == [
            b"userkey2",
            b"appkey2",
            b"60",
            b"3600",
            b"\xe2\x9a\xbd Notification message \xe2\x9a\xbd",
        ]

        # Proof image has content.
        assert len(decoder.parts[-1].content) == 45628

        assert outcome is True
        assert "Sending pushover notification to test" in caplog.text
        assert "Successfully sent pushover notification" in caplog.text


def test_pushover_failure_invalid_configuration(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=[None],
    )

    with caplog.at_level(logging.DEBUG):
        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "Invalid address configuration for target `test'" in caplog.text


def test_pushover_failure_missing_credentials(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=[None, None],
        data={},
    )

    with caplog.at_level(logging.DEBUG):
        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "No pushover credentials configured for target `test'" in caplog.text


@responses.activate
def test_pushover_failure_request_error(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2"],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        # Make remote call bail out.
        module.pushover = mock.MagicMock(side_effect=Exception("something failed"))

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "Sending pushover notification to test" in caplog.text
        assert "Error sending pushover notification: something failed" in caplog.text


@responses.activate
def test_pushover_failure_response_error(srv, caplog):

    module = load_module_from_file("mqttwarn/services/pushover.py")

    item = Item(
        config={},
        target="test",
        addrs=["userkey2", "appkey2"],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        add_failed_mock_response()
        outcome = module.plugin(srv, item)

        assert len(responses.calls) == 1

        assert (
            responses.calls[0].request.url == "https://api.pushover.net/1/messages.json"
        )
        assert (
            responses.calls[0].request.body
            == "user=userkey2&token=appkey2&retry=60&expire=3600&message=%E2%9A%BD+Notification+message+%E2%9A%BD"
        )
        assert responses.calls[0].request.headers["User-Agent"] == "mqttwarn"

        assert responses.calls[0].response.status_code == 400
        assert responses.calls[0].response.text == '{"status": 999}'

        assert outcome is False
        assert "Sending pushover notification to test" in caplog.text
        assert (
            "Error sending pushover notification: b'{\"status\": 999}'" in caplog.text
        )
