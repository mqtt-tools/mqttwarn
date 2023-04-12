# -*- coding: utf-8 -*-
from datetime import datetime

from mqttwarn.model import Service

try:
    import json
except ImportError:
    import simplejson as json

def frigate_events(topic, data, srv=None):
    a = json.loads(data['payload'])['after']
    f = lambda x: (y.replace('_', ' ') for y in x)
    r = {
      'camera': a['camera'],
      'label':  a['sub_label'] or a['label'],
      'current_zones': ', '.join(f(a['current_zones'])),
      'entered_zones': ', '.join(f(a['entered_zones'])),
      'time':   datetime.fromtimestamp(a['frame_time'])
    }
    r.update({
      'title':  f"{r['label']} entered {r['entered_zones']}",
      'format': f"In zones {r['current_zones']} at {r['time']}",
      'click':  f"https://frigate/events?camera={r['camera']}&label={r['label']}&zone={a['entered_zones'][0]}"
    })
    return r


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
    if message.get('type', None) == 'end':
        return True

    # payload must have 'after' key
    elif "after" not in message:
        srv.logging.warning("Frigate event skipped: 'after' missing from payload")
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
