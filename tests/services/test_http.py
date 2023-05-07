# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
from mqttwarn.configuration import Config
from mqttwarn.core import bootstrap, load_services


def test_http_urllib_load_by_alias(caplog):
    """
    Verify loading the `http` service works, even if its implementation module is called `http_urllib`.
    """

    config = Config()
    config.add_section("config:http")
    bootstrap(config=config)
    load_services(["http"])
