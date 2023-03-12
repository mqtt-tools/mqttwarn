# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
"""
This file contains common cases for the Pushsafer plugin, independently
of the used configuration layout variant (v1 vs. v2) within the `addrs` slot.
"""
import pytest

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.services.pushsafer import PushsaferParameters
from mqttwarn.util import load_module_from_file


def test_pushsafer_configuration_empty_failure(srv, caplog, mock_urlopen_success):
    """
    Test Pushsafer service fails when providing an empty `addrs` configuration slot.
    """

    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=None, message="⚽ Notification message ⚽")
    with pytest.raises(ValueError) as ex:
        module.plugin(srv, item)
    assert ex.match("Pushsafer configuration layout empty or invalid. type=NoneType")


def test_pushsafer_configuration_invalid_failure(srv, caplog, mock_urlopen_success):
    """
    Test Pushsafer service fails when providing an invalid `addrs` configuration slot.
    """

    module = load_module_from_file("mqttwarn/services/pushsafer.py")
    item = Item(addrs=42, message="⚽ Notification message ⚽")
    with pytest.raises(ValueError) as ex:
        module.plugin(srv, item)
    assert ex.match("Pushsafer configuration layout empty or invalid. type=int")


def test_pushsafer_parameters_to_dict():
    pp = PushsaferParameters(private_key="foo", device="bar")
    result = pp.to_dict()
    assert isinstance(result, dict)
    assert "private_key" in result
    assert "device" in result
