import json
import logging

from tests import configfile_full
from tests.util import core_bootstrap, send_message


def test_log_invalid_target(caplog):
    """
    Verify that mqttwarn warns appropriately when evaluating
    topic target interpolating yields an invalid log level.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing.
        payload = json.dumps({"loglevel": "invalid", "message": "Foo bar"})
        send_message(topic="test/targets-interpolated", payload=payload)

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert (
            "mqttwarn.services.log",
            40,
            "Cannot invoke service log with level `invalid': 'invalid'",
        ) in caplog.record_tuples
        assert (
            "mqttwarn.core",
            30,
            "Notification of log for `test/targets-interpolated' FAILED or TIMED OUT",
        ) in caplog.record_tuples


def test_log_broken_target(caplog):
    """
    Verify that mqttwarn warns appropriately when evaluating
    topic target interpolating does not yield a list.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing.
        payload = json.dumps({"loglevel": "broken", "message": "Foo bar"})
        send_message(topic="test/targets-interpolated", payload=payload)

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert (
            "mqttwarn.core",
            40,
            "Invoking service 'log' failed: `item.addrs` is not a list",
        ) in caplog.record_tuples
        assert (
            "mqttwarn.core",
            30,
            "Notification of log for `test/targets-interpolated' FAILED or TIMED OUT",
        ) in caplog.record_tuples
