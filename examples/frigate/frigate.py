# -*- coding: utf-8 -*-
from datetime import datetime

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

def frigate_events_filter(topic, message, section, srv=None):
    try:
        message = json.loads(message)
    except:
        message = None
    if message and message.get('type', None) != 'end' and 'after' in message:
        a = message['after']
        return False not in (x in a and (x == 'current_zones' or a[x]) for x in
                                  ('false_positive', 'camera', 'label',
                                   'current_zones', 'entered_zones',
                                   'frame_time'))
    return False
