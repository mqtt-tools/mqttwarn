# -*- coding: utf-8 -*-
# hiveeyes-schwarmalarm function extensions
import re
import json
from pprint import pformat


# ------------------------------------------
#                  Synopsis
# ------------------------------------------
# Setup dependencies::
#
#   pip install xmpppy==0.5.0rc1 jinja2==2.8
#
# Run mqttwarn::
#
#   export MQTTWARNINI=examples/hiveeyes/hiveeyes.ini
#   ./mqttwarn.py
#
# Trigger an alarm by simulating a weight loss event::
#
#   echo '{"wght2": 43.0}' | mosquitto_pub -t hiveeyes/demo/area-42/beehive-1/message-json -l
#   echo '{"wght2": 42.0}' | mosquitto_pub -t hiveeyes/demo/area-42/beehive-1/message-json -l


# ------------------------------------------
#                Configuration
# ------------------------------------------

# Ruleset for monitoring measurement values is defined
# by mapping field names to delta threshold values.
monitoring_rules = {

    # Let's trigger an alarm on a weight loss
    # of 750g or more between two measurements
    'wght2':  0.75,

    # For testing the machinery by
    # monitoring a clock signal
    'second': 0.5,
    }


# ------------------------------------------
#                   Main
# ------------------------------------------

# A dictionary for remembering measurement values
# across a window of two value elements.
history = dict()
history_before = dict()


def format_passthrough(data):
    """
    Stringify complete transformation data from mqttwarn
    to assist debugging as a pass-through formatter.
    """
    return str(data)


def hiveeyes_topic_to_topology(topic):
    """
    Split Hiveeyes MQTT topic path into segments for
    enriching transient message payload inside mqttwarn.
    """
    if type(topic) == str:
        try:
            pattern = r'^(?P<realm>.+?)/(?P<network>.+?)/(?P<gateway>.+?)/(?P<node>.+?)/(?P<field>.+?)$'
            p = re.compile(pattern)
            m = p.match(topic)
            topology = m.groupdict()
        except:
            topology = {}
        return topology
    return None


def hiveeyes_more_data(topic, data, srv):
    """
    Add more data to object, used later
    when formatting the outgoing message.
    """
    more_data = {
        'current': pformat(json.loads(data['payload'])),
        'history': pformat(history_before),
    }
    return more_data


def hiveeyes_schwarmalarm_filter(topic, message):
    """
    Custom filter function to compare two consecutive values
    to trigger notification only if delta is greater threshold.
    """
    global history, history_before

    if not topic.endswith('message-json'):
        return True

    data = dict(json.loads(message).items())

    # Remember current history data for later access from hiveeyes_more_data
    history_before = history.copy()

    alarm = False
    for field in monitoring_rules.keys():

        # Skip if monitored field is not in data payload
        if field not in data:
            continue

        # Read current value and appropriate threshold
        current = data[field]
        threshold = monitoring_rules[field]

        # Compare current with former value and set
        # semaphore if delta is greater threshold
        if field in history:
            former = history[field]
            delta = current - former
            if abs(delta) >= threshold:
                alarm = True

    # Remember current values for next round
    history = data.copy()

    # The filter function should return True if the message should
    # be suppressed, or False if the message should be processed.
    #return False
    return not alarm


# ------------------------------------------
#                   Setup
# ------------------------------------------
# Duplicate of mqttwarn helper method for loading service plugins
# http://code.davidjanes.com/blog/2008/11/27/how-to-dynamically-load-python-code/
def load_module(path):
    import imp
    import hashlib
    try:
        fp = open(path, 'rb')
        return imp.load_source(hashlib.md5(path).hexdigest(), path, fp)
    finally:
        try:
            fp.close()
        except:
            pass

# Mitigate "AttributeError: '_ssl._SSLSocket' object has no attribute 'issuer'"
service_xmpp = load_module('services/xmpp.py')
service_xmpp.xmpppy_monkeypatch_ssl()
