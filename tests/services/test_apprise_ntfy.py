# -*- coding: utf-8 -*-
# (c) 2021-2023 The mqttwarn developers
from unittest import mock
from unittest.mock import call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_by_name


@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_ntfy_success(apprise_asset, apprise_mock, srv, caplog):
    module = load_module_by_name("mqttwarn.services.apprise_multi")

    item = Item(
        addrs=[
            {
                "baseuri": "ntfy://user:password@ntfy.example.org/topic1/topic2?email=test@example.org",
            }
        ],
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        data={"priority": "high", "tags": "foo,bar", "click": "https://httpbin.org/headers"},
    )

    outcome = module.plugin(srv, item)

    assert apprise_mock.mock_calls == [
        call(asset=mock.ANY),
        call().add(
            "ntfy://user:password@ntfy.example.org/topic1/topic2?email=test@example.org"
            "&click=https%3A%2F%2Fhttpbin.org%2Fheaders&priority=high&tags=foo%2Cbar"
        ),
        call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
        call().notify().__bool__(),
    ]

    assert "Successfully sent message using Apprise" in caplog.messages
    assert outcome is True
