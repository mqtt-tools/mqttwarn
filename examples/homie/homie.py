# -*- coding: utf-8 -*-
# Homie function extensions for mqttwarn
import re


# ------------------------------------------
#                  Synopsis
# ------------------------------------------
#
# Run mqttwarn::
#
#   export MQTTWARNINI=examples/homie/homie.ini
#   mqttwarn
#
# Send some homie-like data::
#
#   mosquitto_pub -t homie/bee1/weight/value -m 42.42


def decode_homie_topic(topic):
    """
    Split Homie-style MQTT topic path into segments for
    enriching transformation data inside mqttwarn.
    """
    if type(topic) == str:
        try:
            pattern = r'^(?P<realm>.+?)/(?P<device>.+?)/(?P<node>.+?)/(?P<property>.+?)$'
            p = re.compile(pattern)
            m = p.match(topic)
            topology = m.groupdict()
        except:
            topology = {}
        return topology
    return None

