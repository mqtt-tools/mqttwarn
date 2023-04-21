# -*- coding: utf-8 -*-
"""
Frigate » Forward events and snapshots to Ntfy, using mqttwarn.

https://mqttwarn.readthedocs.io/en/latest/examples/frigate/README.html
"""
import dataclasses
import json
import re
import typing as t
from collections import OrderedDict
from datetime import datetime, timezone

from mqttwarn.context import RuntimeContext
from mqttwarn.model import Service


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

    @staticmethod
    def format_list(value: t.List[str]) -> t.List[str]:
        """
        Format a list for human consumption.
        """
        return [y.replace("_", " ") for y in value]

    @property
    def current_zones_str(self) -> str:
        """
        Serialize list of `current_zones` to string.
        """
        return ", ".join(self.format_list(self.current_zones or []))

    @property
    def entered_zones_str(self) -> str:
        """
        Serialize list of `entered_zones` to string.
        """
        return ", ".join(self.format_list(self.entered_zones or []))

    def to_dict(self) -> t.Dict[str, str]:
        """
        Return Python dictionary from attributes.
        """
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, payload: str) -> "FrigateEvent":
        """
        Decode inbound Frigate event, in JSON format.
        """
        # Decode JSON message.
        after = json.loads(payload)["after"]

        # Decode inbound Frigate event.
        return cls(
            time=datetime.fromtimestamp(after["frame_time"], tz=timezone.utc),
            camera=after["camera"],
            label=after["sub_label"] or after["label"],
            current_zones=after["current_zones"],
            entered_zones=after["entered_zones"],
        )


ContainerType = t.Dict[str, t.Union[str, FrigateEvent]]


def frigate_events(topic: str, data: t.Dict[str, str], srv: Service) -> ContainerType:
    """
    mqttwarn transformation function which computes options to be submitted to ntfy.
    """

    # Decode inbound Frigate event.
    event = FrigateEvent.from_json(data["payload"])

    # Collect outbound ntfy option fields.
    params: ContainerType = OrderedDict()
    params.update(event.to_dict())

    # Also add the event object as a whole, to let downstream templates leverage it.
    params["event"] = event

    return params


def frigate_events_filter(topic: str, payload: str, section: str, srv: Service) -> bool:
    """
    mqttwarn filter function to only use `new` and important `update` Frigate events.

    Additionally, validate more details within the event message,
    specifically the `after` section. For example, skip false positives.

    :return: True if message should be filtered, i.e. notification should be skipped.
    """
    try:
        message = json.loads(payload)
    except json.JSONDecodeError as e:
        srv.logging.warning(f"Can't parse Frigate event message: {e}")
        return True

    # ignore ending messages
    message_type = message.get("type")
    if message_type == "end":
        srv.logging.warning(f"Frigate event skipped, ignoring Message type '{message_type}'")
        return True

    # payload must have 'after' key
    elif "after" not in message:
        srv.logging.warning("Frigate event skipped, 'after' missing from payload")
        return True

    after = message.get("after")

    nonempty_fields = ["false_positive", "camera", "label", "current_zones", "entered_zones", "frame_time"]
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

    # Ignore unimportant `update` events.
    before = message.get("before")
    if message_type == "update" and isinstance(before, dict):
        if before.get("stationary") is True and after.get("stationary") is True:
            srv.logging.warning("Frigate event skipped, object is stationary")
            return True
        elif after["current_zones"] == after["entered_zones"] or (
            before["current_zones"] == after["current_zones"] and before["entered_zones"] == after["entered_zones"]
        ):
            srv.logging.warning("Frigate event skipped, object stayed within same zone")
            return True

    # Evaluate optional skip rules.
    context: RuntimeContext = srv.mwcore["context"]
    frigate_skip_rules = context.config.getdict(section, "frigate_skip_rules")
    for rule in frigate_skip_rules.values():
        do_skip = True
        for field_name, skip_values in rule.items():
            actual_value = after[field_name]
            if isinstance(actual_value, list):
                do_skip = do_skip and all(value in skip_values for value in actual_value)
            else:
                do_skip = do_skip and actual_value in skip_values
        if do_skip:
            srv.logging.warning("Frigate event skipped, object did not enter zone of interest")
            return True

    return False


def frigate_snapshot_decode_topic(topic: str, data: t.Dict[str, str], srv: Service) -> t.Optional[t.Dict[str, str]]:
    """
    Decode Frigate MQTT topic for image snapshots.

    frigate/+/+/snapshot

    See also:
    - https://docs.frigate.video/integrations/mqtt/#frigatecamera_nameobject_namesnapshot
    """
    topology = {}
    if isinstance(topic, str):
        try:
            # TODO: Compile pattern only once, for efficiency reasons.
            pattern = r"^frigate/(?P<camera_name>.+?)/(?P<object_name>.+?)/snapshot$"
            p = re.compile(pattern)
            m = p.match(topic)
            if m:
                topology = m.groupdict()
        except:
            pass
    return topology
