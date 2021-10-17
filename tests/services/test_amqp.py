# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock
from unittest.mock import call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_by_name
from surrogate import surrogate


@surrogate("puka")
@mock.patch("puka.Client", create=True)
def test_amqp_success(mock_puka_client, srv, caplog):
    module = load_module_by_name("mqttwarn.services.amqp")

    exchange, routing_key = ["name_of_exchange", "my_routing_key"]
    item = Item(
        config={"uri": "amqp://user:password@localhost:5672/"},
        target="test",
        addrs=[exchange, routing_key],
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        outcome = module.plugin(srv, item)

        assert mock_puka_client.mock_calls == [
            mock.call("amqp://user:password@localhost:5672/"),
            call().connect(),
            call().wait(mock.ANY),
            call().basic_publish(
                exchange="name_of_exchange",
                routing_key="my_routing_key",
                headers={
                    "content_type": "text/plain",
                    "x-agent": "mqttwarn",
                    "delivery_mode": 1,
                },
                body="⚽ Notification message ⚽",
            ),
            call().wait(mock.ANY),
            call().close(),
        ]

        assert outcome is True
        assert "AMQP publish to test [name_of_exchange/my_routing_key]" in caplog.text
        assert "Successfully published AMQP notification" in caplog.text


@surrogate("puka")
def test_amqp_failure(srv, caplog):
    module = load_module_by_name("mqttwarn.services.amqp")

    exchange, routing_key = ["name_of_exchange", "my_routing_key"]
    item = Item(
        config={"uri": "amqp://user:password@localhost:5672/"},
        target="test",
        addrs=[exchange, routing_key],
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        mock_connection = mock.MagicMock()

        # Make the call to `basic_publish` raise an exception.
        def error(*args, **kwargs):
            raise Exception("something failed")

        mock_connection.basic_publish = error

        with mock.patch("puka.Client", side_effect=[mock_connection], create=True) as mock_client:

            outcome = module.plugin(srv, item)

            assert mock_client.mock_calls == [
                mock.call("amqp://user:password@localhost:5672/"),
            ]
            assert mock_connection.mock_calls == [
                call.connect(),
                call.wait(mock.ANY),
            ]

            assert outcome is False
            assert "AMQP publish to test [name_of_exchange/my_routing_key]" in caplog.text
            assert (
                "Error on AMQP publish to test [name_of_exchange/my_routing_key]: something failed"
                in caplog.text
            )
