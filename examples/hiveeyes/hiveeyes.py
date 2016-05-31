# -*- coding: utf-8 -*-
# hiveeyes-schwarmalarm function extensions for mqttwarn
# https://hiveeyes.org/docs/system/schwarmalarm-mqttwarn.html
import re
import json
from datetime import datetime
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

# Trigger a data-loss event when not receiving any fresh
# data after 20 minutes from a device already seen before.
data_loss_timeout = 20 * 60


# ------------------------------------------
#                   Main
# ------------------------------------------

# A dictionary for remembering measurement values
# across a window of two value elements.
# TODO: Add "network/gateway" information to all bookkeeping data to enable multi-tenancy
history = dict()
history_before = dict()
last_measurement_times = {}
data_loss_state = {}


def format_passthrough(data):
    """
    Stringify complete transformation data from mqttwarn
    to assist debugging as a pass-through formatter.
    """
    return str(data)


def hiveeyes_topic_to_topology(topic):
    """
    Split Hiveeyes MQTT topic path into segments for
    enriching transformation data inside mqttwarn.
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
    Add more data to transformation data object, used later when formatting the outgoing message.
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
    Also, perform data-loss bookkeeping.
    """
    global history, history_before

    if not topic.endswith('message-json'):
        return True

    # Decode message
    data = dict(json.loads(message).items())
    data.update(hiveeyes_topic_to_topology(topic))

    # Data-loss bookkeeping
    origin = '{realm}/{network}/{gateway}/{node}'.format(**data)
    last_measurement_times[origin] = datetime.utcnow()

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


def hiveeyes_dataloss_monitor(srv):
    """
    Periodic thread monitoring all seen devices for data loss events.
    Will submit appropriate data loss notifications using mqttwarn services.
    """

    # Get hold of our own PeriodicThread object to read "period" value
    periodic_threads = srv.mwcore['ptlist']
    me = periodic_threads['hiveeyes_dataloss_monitor']
    interval = me.period

    # Inform operator about this activity
    srv.logging.info('Checking for data-loss (each {interval} seconds)'.format(**locals()))

    # Get hold of mqttwarn method to dispatch notification messages on data loss events
    send_to_targets = srv.mwcore['send_to_targets']

    now = datetime.utcnow()

    # List of all seen data origins (devices).
    # The identifiers are made of essential parts of the MQTT topic.
    origins = last_measurement_times.keys()

    # Iterate all seen devices
    for origin in origins:

        # Signal no data loss as a default
        data_loss_state.setdefault(origin, False)

        # Get timestamp of last valid measurement
        last_measurement_time = last_measurement_times[origin]

        # Compute duration since last valid measurement
        delta = now - last_measurement_time

        # Check if duration is longer than user-defined threshold
        if delta.total_seconds() >= data_loss_timeout:

            # Only act if not already being in state of data loss
            if not data_loss_state[origin]:

                # Set data loss state
                data_loss_state[origin] = True

                # Send out data loss notification
                data = {'description': 'Detected data loss'}
                send_to_targets(
                    section = 'hiveeyes-schwarmalarm',
                    topic   = '{origin}/message-json'.format(origin=origin),
                    payload = json.dumps(data))

        else:
            # Reset data loss state
            data_loss_state[origin] = False

    # TODO: Republish data loss notification to MQTT bus
    #srv.mqttc.publish('data-loss-topic'.format(**locals()), 'data-loss')


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
