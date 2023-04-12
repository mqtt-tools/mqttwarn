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


def frigate_events_filter(topic, message, section, srv: Service=None) -> bool:
    """
    mqttwarn filter function to only use Frigate events of type `new`.
    Additionally, skip, for example, false positives.

    :return: True if message should be filtered, i.e. notification should be skipped.
    """

    # Decode message.
    try:
        message = json.loads(message)
    except:
        message = dict()
    message_type = message.get("type", None)
    srv.logging.info(f"Received Frigate event message with type={message_type}")

    # Determine if message should be used, or not.
    use_message = message_type == "new" and "after" in message

    # Look at more details.
    if use_message:
        after = message["after"]
        if after.get("false_positive") is True:
            srv.logging.info(f"Skipping Frigate event because it's a false positive")
            use_message = False

        # TODO: Honor more details of inbound event message.
        """
        return False not in (x in a and (x == 'current_zones' or a[x]) for x in
                                  ('false_positive', 'camera', 'label',
                                   'current_zones', 'entered_zones',
                                   'frame_time'))
        """
    else:
        use_message = False

    # Inverse logic.
    filter_message = not use_message
    return filter_message
