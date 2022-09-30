# -*- coding: utf-8 -*-
# (c) 2022 The mqttwarn developers
import ssl
from unittest.mock import Mock, call

import mqttwarn.configuration
import pytest


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


# FIXME: Adding `sslv3` raises `AttributeError: module 'ssl' has no attribute 'PROTOCOL_SSLv3'`.
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
