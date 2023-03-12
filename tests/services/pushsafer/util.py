import typing as t
import urllib.request
from urllib.parse import parse_qsl

TEST_TOKEN = "myToken"


def get_reference_data(**more_data):
    data = {
        "m": "⚽ Notification message ⚽",
        "k": "myToken",
        "expire": "3600",
    }
    data.update(more_data)
    return data


def assert_request(request: urllib.request.Request, reference_data: t.Dict[str, str]):
    assert request.full_url == "https://www.pushsafer.com/api"
    actual_data = dict(parse_qsl(request.data.decode("utf-8")))
    msg = f"\nGot:      {actual_data}\nExpected: {reference_data}"
    assert actual_data == reference_data, msg
