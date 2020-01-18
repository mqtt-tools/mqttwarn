# -*- coding: utf-8 -*-
# hiveeyes-schwarmalarm function extensions for mqttwarn
# https://hiveeyes.org/docs/system/schwarmalarm-mqttwarn.html
from builtins import object
from past.builtins import cmp
from builtins import str
import re
import json
from datetime import datetime
from pprint import pformat, pprint
from collections import deque, defaultdict


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
#   mqttwarn
#
# Trigger an alarm by simulating a weight loss event::
#
#   echo '{"wght2": 43.0}' | mosquitto_pub -t hiveeyes/demo/area-42/beehive-1/data.json -l
#   echo '{"wght2": 42.0}' | mosquitto_pub -t hiveeyes/demo/area-42/beehive-1/data.json -l


# ------------------------------------------
#                Configuration
# ------------------------------------------

# Ruleset for monitoring measurement values is defined
# by mapping field names to delta threshold values.
monitoring_rules = {

    # Let's trigger an alarm on a weight loss
    # of 750g or more between two measurements
    'wght2':  {'threshold': 0.75, 'unit': 'kilo'},

    # For testing the machinery by
    # monitoring a clock signal
    'second': {'threshold': 0.5, 'unit': 'second'},
    }

# Trigger a data-loss event when not receiving any fresh
# data after 20 minutes from a device already seen before.
data_loss_timeout = 20 * 60

# Just a hack to give the anonymous data source of "Labhive One" a better name
dashboard_aliases = {
    '25a0e5df-9517-405b-ab14-cb5b514ac9e8': 'hiveeyes-labs-wedding',
}


# ------------------------------------------
#                   Main
# ------------------------------------------

# Data structure for remembering measurement values across a variable window size.
class HistoricData(object):

    # How many data points to remember
    backlog = 20

    def __init__(self):
        series_factory = lambda: deque(maxlen=HistoricData.backlog)

        # Some data containers for remembering ...

        # Inbound data payload fragments
        self.fragments = defaultdict(series_factory)

        # All attributes aggregated across consecutive data payload fragments
        # This is actually used for threshold comparison
        self.history = defaultdict(series_factory)

        # Arbitrary node states like "data-loss"
        self.states = defaultdict(dict)

        # Most recent moment of data acquisition per node
        self.moments = {}

# A single data container instance to rule them all
hdata = HistoricData()


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

    if not (topic.endswith('data.json') or topic.endswith('message-json')):
        return

    message = data['payload']

    # Decode message (redundant with "hiveeyes_schwarmalarm_filter")
    mdata = dict(json.loads(message).items())
    tdata = mdata.copy()
    tdata.update(hiveeyes_topic_to_topology(topic))

    # Compute bookkeeping key for multi-tenancy
    origin = '{realm}/{network}/{gateway}/{node}'.format(**tdata)

    condition = {'current': None, 'previous': None}

    # Get current and previous measurements
    fragments = condition.copy()
    try:
        fragments['current'] = hdata.fragments[origin][-1]
    except IndexError:
        pass
    try:
        fragments['previous'] = hdata.fragments[origin][-2]
    except IndexError:
        pass

    history = condition.copy()
    try:
        history['current'] = hdata.history[origin][-1]
    except IndexError:
        pass
    try:
        history['previous'] = hdata.history[origin][-2]
    except IndexError:
        pass

    # Compute Grafana dashboard name from simple map, fall back
    # to network identifier as this is the default of Kotori's GrafanaManager.
    dashboard = dashboard_aliases.get(tdata['network'], tdata['network'])

    more_data = {

        # current/previous data
        'fragments': fragments,
        'history': history,

        # more enrichment
        'dashboard': dashboard,

        # utilities
        'pformat': pformat,
    }

    # Also push the "event" state into the template machinery
    # This is used for displaying a preformatted description message to humans
    if 'event' in hdata.states[origin]:
        more_data.update(hdata.states[origin]['event'])

    return more_data


def hiveeyes_schwarmalarm_filter(topic, message):
    """
    Custom filter function to compare two consecutive values
    to trigger notification only if delta is greater threshold.
    Also, perform data-loss bookkeeping.
    """

    if not (topic.endswith('data.json') or topic.endswith('message-json')):
        return True

    # Decode message (redundant with "hiveeyes_more_data")
    mdata = dict(json.loads(message).items())
    tdata = mdata.copy()
    tdata.update(hiveeyes_topic_to_topology(topic))

    # Compute bookkeeping key for multi-tenancy
    origin = '{realm}/{network}/{gateway}/{node}'.format(**tdata)

    # Data-loss bookkeeping
    hdata.moments[origin] = datetime.utcnow()

    # Get most recent measurement from series
    try:
        history = hdata.history[origin][-1].copy()
    except IndexError:
        history = {}

    alarm = False
    for field in monitoring_rules.keys():

        # Skip if monitored field is not in data payload
        if field not in tdata:
            continue

        # Read current value and appropriate threshold
        current = tdata[field]
        threshold = monitoring_rules[field]['threshold']

        # Compare current with former value and set
        # semaphore if delta is greater threshold
        if field in history:
            previous = history[field]
            delta = float(current) - float(previous)
            delta_nosign = abs(delta)
            if delta_nosign >= threshold:

                # Set event state outcome / semaphore
                alarm = True

                # Format description message for displaying to humans, e.g.
                # »Sensor value "wght2" gained 1.42 kilos.«
                unit = monitoring_rules[field].get('unit', 'point')
                verb = delta != 0 and (cmp(delta, 0) == 1 and 'gained' or 'lost') or 'did not change'
                description = 'Sensor value "{field}" {verb} {delta_nosign} {unit}s.'.format(
                    field=field, verb=verb, delta_nosign=delta_nosign, unit=unit)
                hdata.states[origin]['event'] = {'field': field, 'delta': delta, 'description': description}
            else:
                # Reset event state
                if 'event' in hdata.states[origin]:
                    del hdata.states[origin]['event']

    # Remember current values for next round
    hdata.fragments[origin].append(mdata)

    history.update(mdata)
    hdata.history[origin].append(history)

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
    origins = hdata.moments.keys()

    # Iterate all seen devices
    for origin in origins:

        # Signal no data loss as a default
        hdata.states[origin].setdefault('data-loss', False)

        # Get timestamp of last valid measurement
        last_moment = hdata.moments[origin]

        # Compute duration since last valid measurement
        delta = now - last_moment

        # Check if duration is longer than user-defined threshold
        if delta.total_seconds() >= data_loss_timeout:

            # Only act if not already being in state of data loss
            if 'data-loss' not in hdata.states[origin] or not hdata.states[origin]['data-loss']:

                # Set data loss state
                hdata.states[origin]['data-loss'] = True

                # Send out data loss notification
                data = {'description': 'Detected data loss.'}
                send_to_targets(
                    section = 'hiveeyes-schwarmalarm',
                    topic   = '{origin}/notification.json'.format(origin=origin),
                    payload = json.dumps(data))

        else:
            # Reset data loss state
            hdata.states[origin]['data-loss'] = False

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

