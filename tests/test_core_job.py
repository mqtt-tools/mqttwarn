# -*- coding: utf-8 -*-
# (c) 2018-2023 The mqttwarn developers
from mqttwarn.core import process_job
from mqttwarn.model import ProcessorItem
from tests.util import core_bootstrap


def test_process_job_without_target_addrs(tmp_ini, caplog):
    """
    Verify job dispatching w/o any target address information works (2021-10-18 [amo]).
    """

    tmp_ini.write_text(
        """
[defaults]
launch = noop

[config:noop]
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Define and process the job.
    item = ProcessorItem(
        service="noop",
        target=None,
        message="foo",
        data={},
    )
    process_job(item.to_job())

    assert "Successfully sent message using noop" in caplog.messages


def test_process_job_with_invalid_priority(tmp_ini, caplog):
    """
    Verify invalid topic priority will emit a corresponding warning.
    """

    tmp_ini.write_text(
        """
[defaults]
launch = noop

[config:noop]

[testdrive/invalid-priority]
priority = invalid
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Define and process the job.
    item = ProcessorItem(
        service="noop",
        target=None,
        section="testdrive/invalid-priority",
        message="foo",
        data={},
    )
    process_job(item.to_job())

    assert "Failed to determine the priority, defaulting to zero" in caplog.messages
    assert "ValueError: invalid literal for int() with base 10: 'invalid'" in caplog.text


def test_process_job_with_failing_template_rendering(tmp_ini, caplog):
    """
    When rendering a template fails, a corresponding warning should be emitted.
    """

    tmp_ini.write_text(
        """
[defaults]
launch = noop

[config:noop]

[testdrive/template]
template = unknown.jinja
targets = noop
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Define and process the job.
    item = ProcessorItem(
        service="noop",
        target=None,
        section="testdrive/template",
        message="foo",
        data={},
    )
    process_job(item.to_job())

    assert "Rendering template failed: unknown.jinja" in caplog.messages
    assert "TemplateNotFound: unknown.jinja" in caplog.text


def test_process_job_with_empty_payload_is_suppressed(tmp_ini, caplog):
    """
    Verify job dispatching with an empty message payload will suppress it.
    """

    tmp_ini.write_text(
        """
[defaults]
launch = noop

[config:noop]
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Define and process the job.
    item = ProcessorItem(
        service="noop",
        target=None,
        message="",
        data={},
    )
    process_job(item.to_job())

    assert "Notification suppressed. Reason: Payload is empty. service=noop, topic=None" in caplog.messages
