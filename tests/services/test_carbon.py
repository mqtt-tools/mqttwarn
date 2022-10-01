# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
from unittest import mock
from unittest.mock import Mock, call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


def test_carbon_success_metric_value_timestamp(mocker, srv, caplog):

    item = Item(
        target="test",
        addrs=["localhost", 2003],
        message="foo 42.42 1623887596",
        data={},
    )

    module = load_module_from_file("mqttwarn/services/carbon.py")

    socket_mock = mocker.patch("socket.socket")

    outcome = module.plugin(srv, item)
    assert socket_mock.mock_calls == [
        call(),
        call().connect(("localhost", 2003)),
        call().sendall("foo 42.42 1623887596\n"),
        call().close(),
    ]

    assert outcome is True
    assert "Sending to carbon: foo 42.42 1623887596" in caplog.messages


def test_carbon_success_metric_value(mocker, srv, caplog):

    item = Item(target="test", addrs=["localhost", 2003], message="foo 42.42", data={})

    module = load_module_from_file("mqttwarn/services/carbon.py")

    socket_mock = mocker.patch("socket.socket")

    outcome = module.plugin(srv, item)
    assert socket_mock.mock_calls == [
        call(),
        call().connect(("localhost", 2003)),
        call().sendall(mock.ANY),
        call().close(),
    ]

    assert outcome is True
    assert "Sending to carbon: foo 42.42" in caplog.text


def test_carbon_success_value(mocker, srv, caplog):

    item = Item(target="test", addrs=["localhost", 2003], message="42.42", data={})

    module = load_module_from_file("mqttwarn/services/carbon.py")

    socket_mock = mocker.patch("socket.socket")

    outcome = module.plugin(srv, item)
    assert socket_mock.mock_calls == [
        call(),
        call().connect(("localhost", 2003)),
        call().sendall(mock.ANY),
        call().close(),
    ]

    assert outcome is True
    assert "Sending to carbon: ohno 42.42" in caplog.text


def test_carbon_success_value_metric_from_topic(mocker, srv, caplog):

    item = Item(
        target="test",
        addrs=["localhost", 2003],
        message="42.42",
        data={"topic": "foo/bar"},
    )

    module = load_module_from_file("mqttwarn/services/carbon.py")

    socket_mock = mocker.patch("socket.socket")

    outcome = module.plugin(srv, item)
    assert socket_mock.mock_calls == [
        call(),
        call().connect(("localhost", 2003)),
        call().sendall(mock.ANY),
        call().close(),
    ]

    assert outcome is True
    assert "Sending to carbon: foo.bar 42.42" in caplog.text


def test_carbon_success_value_metric_from_topic_with_leading_slash(mocker, srv, caplog):

    item = Item(
        target="test",
        addrs=["localhost", 2003],
        message="42.42",
        data={"topic": "/foo/bar"},
    )

    module = load_module_from_file("mqttwarn/services/carbon.py")

    socket_mock = mocker.patch("socket.socket")

    outcome = module.plugin(srv, item)
    assert socket_mock.mock_calls == [
        call(),
        call().connect(("localhost", 2003)),
        call().sendall(mock.ANY),
        call().close(),
    ]

    assert outcome is True
    assert "Sending to carbon: foo.bar 42.42" in caplog.text


def test_carbon_failure_invalid_configuration(srv, caplog):

    item = Item(target="test", addrs=["172.16.153.110", "foobar"])

    module = load_module_from_file("mqttwarn/services/carbon.py")

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Configuration for target `carbon' is incorrect" in caplog.messages


def test_carbon_failure_empty_message(srv, caplog):

    item = Item(target="test", addrs=["172.16.153.110", 2003])

    module = load_module_from_file("mqttwarn/services/carbon.py")

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "target `carbon': cannot split string" in caplog.messages


def test_carbon_failure_invalid_message_format(srv, caplog):

    item = Item(
        target="test",
        addrs=["172.16.153.110", 2003],
        message="foo bar baz qux",
        data={},
    )

    module = load_module_from_file("mqttwarn/services/carbon.py")

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "target `carbon': error decoding message" in caplog.messages


def test_carbon_failure_connect(mocker, srv, caplog):

    item = Item(
        target="test",
        addrs=["localhost", 2003],
        message="foo 42.42 1623887596",
        data={},
    )

    module = load_module_from_file("mqttwarn/services/carbon.py")

    socket_mock = mocker.patch("socket.socket")

    # Inject exception to be raised on `socket.connect`.
    socket_mock.return_value = Mock(**{"connect.side_effect": Exception("something failed")})

    outcome = module.plugin(srv, item)
    assert socket_mock.mock_calls == [call(), call().connect(("localhost", 2003))]

    assert outcome is False
    assert "Sending to carbon: foo 42.42 1623887596" in caplog.messages
    assert "Cannot send to carbon service localhost:2003: something failed" in caplog.messages
