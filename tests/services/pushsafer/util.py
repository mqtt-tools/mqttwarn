import typing as t
import urllib.request
from urllib.parse import parse_qsl

TEST_TOKEN = "myToken"


def get_reference_data(**more_data):
    data = {
        "m": "⚽ Notification message ⚽",
        "k": "myToken",
    }
    data.update(more_data)
    return data


def assert_request(request: urllib.request.Request, reference_data: t.Dict[str, str]):
    assert request.full_url == "https://www.pushsafer.com/api"
    if isinstance(request.data, bytes):
        payload = request.data
    elif hasattr(request.data, "read"):
        payload = request.data.read()  # type: ignore[union-attr]
    else:
        raise ValueError(f"Something went wrong. Could not decode `request.data`: {request.data}")
    actual_data = dict(parse_qsl(payload.decode("utf-8"), keep_blank_values=True))
    msg = f"\nGot:      {actual_data}\nExpected: {reference_data}"
    assert actual_data == reference_data, msg
