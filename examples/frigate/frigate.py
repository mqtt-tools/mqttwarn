# -*- coding: utf-8 -*-
import dataclasses
from datetime import datetime
import typing as t

from mqttwarn.context import RuntimeContext
from mqttwarn.model import Service

try:
    import json
except ImportError:
    import simplejson as json


@dataclasses.dataclass
class FrigateEvent:
    """
    Manage inbound event data received from Frigate.
    """
    time: datetime
    camera: str
    label: str
    current_zones: t.List[str]
    entered_zones: t.List[str]

    def f(self, value):
        return [y.replace('_', ' ') for y in value]

    @property
    def current_zones_str(self):
        return ', '.join(self.f(self.current_zones))

    @property
    def entered_zones_str(self):
        return ', '.join(self.f(self.entered_zones))

    def to_dict(self) -> t.Dict[str, str]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class NtfyParameters:
    """
    Manage outbound parameter data for Apprise/Ntfy.
    """
    title: str
    format: str
    click: str
    attach: t.Optional[str] = None

    def to_dict(self) -> t.Dict[str, str]:
        data = dataclasses.asdict(self)
        data = {k: v for (k, v) in data.items() if v is not None}
        return data


def frigate_events(topic, data, srv: Service):
    """
    mqttwarn transformation function which computes options to be submitted to Apprise/Ntfy.
    """

    # Acceptable hack to get attachment filename template from service configuration.
    context: RuntimeContext = srv.mwcore["context"]
    service_config = context.get_service_config("apprise-ntfy")
    filename_template = service_config.get("filename_template")

    # Decode JSON message.
    after = json.loads(data['payload'])['after']

    # Collect details from inbound Frigate event.
    event = FrigateEvent(
        time=datetime.fromtimestamp(after['frame_time']),
        camera=after['camera'],
        label=after['sub_label'] or after['label'],
        current_zones=after['current_zones'],
        entered_zones=after['entered_zones'],
    )

    # Interpolate event data into attachment filename template.
    attach_filename = filename_template.format(**event.to_dict())

    # Compute parameters for outbound Apprise / Ntfy URL.
    ntfy_parameters = NtfyParameters(
        title=f"{event.label} entered {event.entered_zones_str}",
        format=f"In zones {event.current_zones_str} at {event.time}",
        click=f"https://frigate/events?camera={event.camera}&label={event.label}&zone={event.entered_zones[0]}",
        #attach=attach_filename,
    )
    return ntfy_parameters.to_dict()


def frigate_events_filter(topic, message, section, srv: Service):
    """
    mqttwarn filter function to only use Frigate events of type `new`.

    Additionally, validate more details within the event message,
    specifically the `after` section. For example, skip false positives.

    :return: True if message should be filtered, i.e. notification should be skipped.
    """
    try:
        message = json.loads(message)
    except json.JSONDecodeError as e:
        srv.logging.warning(f"Can't parse Frigate event message: {e}")
        return True

    # ignore ending messages
    message_type = message.get('type', None)
    if message_type == 'end':
        srv.logging.warning(f"Frigate event skipped, ignoring Message type '{message_type}'")
        return True

    # payload must have 'after' key
    elif "after" not in message:
        srv.logging.warning("Frigate event skipped, 'after' missing from payload")
        return True

    after = message.get('after')

    nonempty_fields = ['false_positive', 'camera', 'label', 'current_zones', 'entered_zones', 'frame_time']
    for field in nonempty_fields:

        # Validate field exists.
        if field not in after:
            srv.logging.warning(f"Frigate event skipped, missing field: {field}")
            return True

        value = after.get(field)

        # We can ignore if `current_zones` is empty.
        if field == "current_zones":
            continue

        # Check if it's a false positive.
        if field == "false_positive":
            if value is True:
                srv.logging.warning("Frigate event skipped, it is a false positive")
                return True
            else:
                continue

        # All other keys should be present and have values.
        if not value:
            srv.logging.warning(f"Frigate event skipped, field is empty: {field}")
            return True

    return False
