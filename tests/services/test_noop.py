# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
from mqttwarn.model import ProcessorItem
from mqttwarn.util import load_module_by_name


def test_noop_success(srv, caplog):
    module = load_module_by_name("mqttwarn.services.noop")

    item = ProcessorItem()
    outcome = module.plugin(srv, item)

    assert outcome is True
    assert "Successfully sent message using noop" in caplog.messages


def test_noop_failure(srv, caplog):
    module = load_module_by_name("mqttwarn.services.noop")

    item = ProcessorItem(message="fail")
    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Failed sending message using noop" in caplog.messages
