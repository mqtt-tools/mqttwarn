# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
from unittest.mock import ANY, Mock, call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_by_name


def test_amqp_success(srv, mocker, caplog):
    module = load_module_by_name("mqttwarn.services.amqp")

    exchange, routing_key = ["name_of_exchange", "my_routing_key"]
    item = Item(
        config={"uri": "amqp://user:password@localhost:5672/"},
        target="test",
        addrs=[exchange, routing_key],
        message="⚽ Notification message ⚽",
    )

    mock_puka_client = mocker.patch("puka.Client", create=True)

    outcome = module.plugin(srv, item)

    assert mock_puka_client.mock_calls == [
        call("amqp://user:password@localhost:5672/"),
        call().connect(),
        call().wait(ANY),
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
        call().wait(ANY),
        call().close(),
    ]

    assert outcome is True
    assert "AMQP publish to test [name_of_exchange/my_routing_key]" in caplog.messages
    assert "Successfully published AMQP notification" in caplog.messages


def test_amqp_failure(srv, mocker, caplog):
    module = load_module_by_name("mqttwarn.services.amqp")

    exchange, routing_key = ["name_of_exchange", "my_routing_key"]
    item = Item(
        config={"uri": "amqp://user:password@localhost:5672/"},
        target="test",
        addrs=[exchange, routing_key],
        message="⚽ Notification message ⚽",
    )

    mock_connection = Mock(**{"basic_publish.side_effect": Exception("something failed")})
    mock_client = mocker.patch("puka.Client", side_effect=[mock_connection], create=True)

    outcome = module.plugin(srv, item)

    assert mock_client.mock_calls == [
        call("amqp://user:password@localhost:5672/"),
    ]
    assert mock_connection.mock_calls == [
        call.connect(),
        call.wait(ANY),
        call.basic_publish(
            exchange="name_of_exchange",
            routing_key="my_routing_key",
            headers={"content_type": "text/plain", "x-agent": "mqttwarn", "delivery_mode": 1},
            body="⚽ Notification message ⚽",
        ),
    ]

    assert outcome is False
    assert "AMQP publish to test [name_of_exchange/my_routing_key]" in caplog.messages
    assert "Error on AMQP publish to test [name_of_exchange/my_routing_key]: something failed" in caplog.messages
