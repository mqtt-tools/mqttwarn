# -*- coding: utf-8 -*-
# (c) 2022 The mqttwarn developers
import os
import re
import ssl
from unittest.mock import Mock, call, patch

import pytest

import mqttwarn.configuration
from mqttwarn.configuration import load_configuration
from tests import configfile_better_addresses, configfile_with_variables


def test_config_with_ssl():
    """
    The `ssl` package should be available by default.
    """
    assert mqttwarn.configuration.HAVE_TLS is True


def test_config_without_ssl(without_ssl, caplog):
    """
    Verify `mqttwarn` also works without the `ssl` package.
    """
    assert mqttwarn.configuration.HAVE_TLS is False

    with pytest.raises(SystemExit) as ex:
        mqttwarn.configuration.Config()
    assert ex.value.code == 2
    assert "TLS parameters set but no TLS available (SSL)" in caplog.messages


def test_config_notls_is_default():
    """
    By default, SSL/TLS is not enabled.
    """
    config = mqttwarn.configuration.Config()
    assert config.tls is False


@pytest.mark.parametrize("tls_version", ["tlsv1", "tlsv1_1", "tlsv1_2"])
def test_config_tls_active(tls_version):
    """
    When obtaining the `tls` or `ca_certs` options, TLS will be enabled.
    """
    config = mqttwarn.configuration.Config(defaults={"ca_certs": "/path/to/ca-certs.pem", "tls_version": tls_version})
    assert config.tls is True
    assert isinstance(config.tls_version, ssl._SSLMethod)


def test_config_g_error_handling(mocker):
    """
    Verify the behavior of the `Config.g` method.
    """
    m: Mock = mocker.patch("mqttwarn.configuration.Config.get", side_effect=TypeError("Something failed"))
    config = mqttwarn.configuration.Config()
    with pytest.raises(TypeError) as ex:
        config.g("foo", "bar")
    assert ex.match("Something failed")
    assert m.mock_calls == [
        call("foo", "bar"),
    ]


def test_config_better_addresses_apprise():
    """
    Verify reading configuration files with nested dictionaries.
    """
    config = load_configuration(configfile_better_addresses)
    apprise_service_targets = config.getdict("config:apprise", "targets")
    assert apprise_service_targets["demo-mailto"][0]["recipients"] == ["foo@example.org", "bar@example.org"]


def test_config_better_addresses_pushsafer():
    """
    Verify reading configuration files with nested dictionaries.
    """
    config = load_configuration(configfile_better_addresses)
    apprise_service_targets = config.getdict("config:pushsafer", "targets")
    assert apprise_service_targets["basic"]["private_key"] == "3SAz1a2iTYsh19eXIMiO"
    assert apprise_service_targets["nagios"]["private_key"] == "3SAz1a2iTYsh19eXIMiO"
    assert apprise_service_targets["nagios"]["device"] == "52|65|78"
    assert apprise_service_targets["nagios"]["priority"] == 2
    assert apprise_service_targets["tracking"]["device"] == "gs23"


@patch.dict(os.environ, {"HOSTNAME": "example.com", "PORT": "3000", "USERNAME": "bob", "LOG_FILE": "/tmp/out.log"})
def test_config_expand_variables():
    """
    Verify reading configuration file expands variables.
    """
    config = load_configuration(configfile_with_variables)
    assert config.hostname == "example.com"
    assert config.port == 3000
    assert config.username == "bob"
    assert config.password == "secret-password"
    assert config.getdict("config:file", "targets")["mylog"][0] == "/tmp/out.log"


@pytest.mark.parametrize(
    "input, expected",
    [
        ("my-password", "my-password"),
        ("$SRC_1:PASSWORD_1", "my-password"),
        ("$SRC_1:PASSWORD_2", "super-secret"),
        ("-->$SRC_1:PASSWORD_1<--", "-->my-password<--"),
        ("$SRC_2:PASSWORD_1", "p4ssw0rd"),
        ("$SRC_1:PÄSSWÖRD_3", "non-ascii-secret"),
        ("${SRC_1:PASSWORD_1}", "my-password"),
        ("${SRC_1:/path/to/password.txt}", "file-contents"),
        ("${SRC_1:PASSWORD_1} ${SRC_1:PASSWORD_2}", "my-password super-secret"),
        ("$SRC_1:PASSWORD_1 ${SRC_1:/path/to/password.txt} $SRC_1:PASSWORD_1", "my-password file-contents my-password"),
        (
            "${SRC_1:/path/to/password.txt} $SRC_1:PASSWORD_1 ${SRC_1:/path/to/password.txt}",
            "file-contents my-password file-contents",
        ),
        ("/$SRC_1:PASSWORD_1/$SRC_1:PASSWORD_2/foo.txt", "/my-password/super-secret/foo.txt"),
    ],
)
def test_expand_vars_ok(input, expected):
    """
    Verify that `expand_vars` expands variables in configuration.
    """

    def create_source(variables):
        return lambda name: variables[name]

    sources = {
        "SRC_1": create_source(
            {
                "PASSWORD_1": "my-password",
                "PASSWORD_2": "super-secret",
                "PÄSSWÖRD_3": "non-ascii-secret",
                "/path/to/password.txt": "file-contents",
            }
        ),
        "SRC_2": create_source(
            {
                "PASSWORD_1": "p4ssw0rd",
            }
        ),
    }
    expanded = mqttwarn.configuration.expand_vars(input, sources)
    assert expanded == expected


def test_expand_vars_variable_type_not_supported():
    """
    Verify that `expand_vars` raises error when variable type is not supported.
    """
    with pytest.raises(
        KeyError, match=re.escape("$DOES_NOT_EXIST:VARIABLE: Variable type 'DOES_NOT_EXIST' not supported")
    ):
        mqttwarn.configuration.expand_vars("-->$DOES_NOT_EXIST:VARIABLE<--", {})


def test_expand_vars_variable_not_found():
    """
    Verify that `expand_vars` raises error when variable is not in source.
    """

    def empty_source(name):
        raise KeyError("Variable not found")

    with pytest.raises(KeyError, match=re.escape("$SRC_1:VARIABLE: 'Variable not found'")):
        mqttwarn.configuration.expand_vars("-->$SRC_1:VARIABLE<--", {"SRC_1": empty_source})
