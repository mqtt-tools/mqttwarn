#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
import logging
import signal
import sys
import time
try:
    import json
except ImportError:
    import simplejson as json
import Queue
import threading
import imp
try:
    import hashlib
    md = hashlib.md5
except ImportError:
    import md5
    md = md5.new
import os
import socket

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>, Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

# script name (without extension) used for config/logfile names
SCRIPTNAME = os.path.splitext(os.path.basename(__file__))[0]

CONFIGFILE = os.getenv(SCRIPTNAME.upper() + 'CONF', SCRIPTNAME + '.conf')
LOGFILE    = os.getenv(SCRIPTNAME.upper() + 'LOG', SCRIPTNAME + '.log')

# load configuration
conf = {}
try:
    execfile(CONFIGFILE, conf)
except Exception, e:
    print "Cannot load %s: %s" % (CONFIGFILE, str(e))
    sys.exit(2)

LOGLEVEL = conf.get('loglevel', logging.DEBUG)
LOGFORMAT = conf.get('logformat', '%(asctime)-15s %(message)s')

MQTT_HOST = conf.get('broker', 'localhost')
MQTT_PORT = int(conf.get('port', 1883))
MQTT_LWT = conf.get('lwt', None)

# initialise logging    
logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
logging.info("Starting %s" % SCRIPTNAME)
logging.info("INFO MODE")
logging.debug("DEBUG MODE")

q_in = Queue.Queue(maxsize=0)
num_workers = 1

# Class with helper functions which is passed to each plugin
# and its global instantiation
class Service(object):
    def __init__(self, mqttc, logging):
        self.mqttc    = mqttc
        self.logging  = logging
        self.SCRIPTNAME = SCRIPTNAME
srv = Service(None, None)

service_plugins = {}

# http://stackoverflow.com/questions/1305532/
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    def __repr__(self):
        return '<%s>' % str("\n ".join("%s: %s" % (k, repr(v)) for (k, v) in self.__dict__.iteritems()))
    def get(self, key, default=None):
        if key in self.__dict__ and self.__dict__[key] is not None:
            return self.__dict__[key]
        else:
            return default

    def enum(self):
        item = {}
        for (k, v) in self.__dict__.iteritems():
            item[k] = v
        return item

# initialise MQTT broker connection
mqttc = paho.Client(SCRIPTNAME, clean_session=False)

def on_connect(mosq, userdata, result_code):
    logging.debug("Connected to MQTT broker, subscribing to topics...")
    for topic in conf['topicmap'].keys():
        logging.debug("Subscribing to %s" % topic)
        mqttc.subscribe(topic, 0)

def get_targets(target, targetkey):
    ''' If no specific target then return ALL targets for
        this key. '''
    if target is None:
        return conf[targetkey].keys()

    return [target]

def get_title(topic):
    ''' Find the "title" (for pushover) or "subject" (for smtp)
        from the topic. '''
    title = None
    if 'titlemap' in conf:
        for key in conf['titlemap'].keys():
            if paho.topic_matches_sub(key, topic):
                title = conf['titlemap'][key]
                break
    return title

def get_priority(topic):
    ''' Find the "priority" (for pushover)
        from the topic. '''
    priority = None
    if 'prioritymap' in conf:
        for key in conf['prioritymap'].keys():
            if paho.topic_matches_sub(key, topic):
                priority = conf['prioritymap'][key]
                break
    return priority

def get_messagefmt(topic):
    ''' Find the message format from the topic '''
    fmt = None
    if 'formatmap' in conf:
        for key in conf['formatmap'].keys():
            if paho.topic_matches_sub(key, topic):
                fmt = conf['formatmap'][key]
                break
    return fmt

def get_messagefilter(topic):
    ''' Find the message filter from the topic '''
    filter = None
    if 'filtermap' in conf:
        for key in conf['filtermap'].keys():
            if paho.topic_matches_sub(key, topic):
                filter = conf['filtermap'][key]
                break
    return filter

def get_topic_data(topic):
    ''' Find out if there is a function in topicdatamap{} for
        adding topic into data. If there is, invoke that
        and return a dict of it '''
    data = None
    if 'topicdatamap' in conf:
        for key in conf['topicdatamap'].keys():
            if paho.topic_matches_sub(key, topic):
                func = conf['topicdatamap'][key]
                if hasattr(func, '__call__'):
                    try:
                        data = func(topic)
                    except Exception, e:
                        logging.warn("Cannot invoke func(%s): %s" % (topic, str(e)))
                break
    return data

class Job(object):
    def __init__(self, prio, service, topic, payload, target):
        self.prio       = prio
        self.service    = service
        self.topic      = topic
        self.payload    = payload
        self.target     = target

        logging.debug("New `%s:%s' job: %s" % (service, target, topic))
        return
    def __cmp__(self, other):
        return cmp(self.prio, other.prio)


def on_message(mosq, userdata, msg):
    """
    Message received from the broker
    """

    # FIXME: skip retained messages

    topic = msg.topic
    payload = str(msg.payload)
    logging.debug("Message received on %s: %s" % (topic, payload))

    # Check for any message filters
    filter = get_messagefilter(topic)
    if hasattr(filter, '__call__'):
        try:
            if filter(topic, payload):
                logging.debug("Message on %s has been filtered. Skipping." % (topic))
                return
        except Exception, e:
            logging.warn("Cannot invoke filter(%s): %s" % (topic, str(e)))

    # Try to find matching settings for this topic
    for key in conf['topicmap'].keys():
        if paho.topic_matches_sub(key, topic):
            targetlist = conf['topicmap'][key]
            logging.debug("Topic [%s] going to %s" % (topic, targetlist))

            for t in targetlist:
                # Each target is either "service" or "service:target"
                # If no target specified then notify ALL targets
                service = t
                target = None

                # Check if this is for a specific target
                if t.find(':') != -1:
                    try:
                        service, target = t.split(':', 2)
                    except:
                        logging.warn("Invalid target %s - should be 'service:target'" % (t))
                        continue

                if not service in service_plugins:
                    logging.error("Invalid configuration: topic %s points to non-existing service %s" % (topic, service))
                    return

                for sendto in get_targets(target, service + '_targets'):
                    job = Job(1, service, topic, payload, sendto)

                    # Put the job on the queue
                    q_in.put(job)
    return

def on_disconnect(mosq, userdata, result_code):
    """
    Handle disconnections from the broker
    """
    if result_code == 0:
        logging.info("Clean disconnection")
    else:
        logging.info("Unexpected disconnection! Reconnecting in 5 seconds...")
        logging.debug("Result code: %s", result_code)
        time.sleep(5)
        connect()

def processor():
    """
    Queue runner. Pull a job from the queue, find the module in charge
    of handling the service, and invoke the module's plugin to do so.
    """

    while True:
        job = q_in.get()

        service = job.service
        target  = job.target

        logging.debug("processor is handling: `%s' for %s" % (service, target))

        item = {
            'service'       : service,
            'target'        : target,
            'config'        : conf[service + '_config'],
            'addrs'         : conf[service + '_targets'][target],
            'topic'         : job.topic,
            'payload'       : job.payload,
            'fmt'           : get_messagefmt(job.topic),
            'data'          : None,
            'message'       : job.payload     # might get replaced with a formatted payload
        }
        item['title']       = get_title(job.topic)
        item['priority']    = get_priority(job.topic)

        transform_data = {}
        topic_data = get_topic_data(job.topic)
        if topic_data is not None and type(topic_data) == dict:
            transform_data = dict(transform_data.items() + topic_data.items())

        # Attempt to decode the payload from JSON. If it's possible, add
        # the JSON keys into item to pass to the plugin, and create the
        # outgoing (i.e. transformed) message.

        try:
            data = json.loads(job.payload)
            transform_data = dict(transform_data.items() + data.items())
            item['data'] = dict(transform_data.items())

            # See if there is a formatter for this topic. If so, create an
            # item containing the transformed payload. If that fails, use
            # the original payload

            text = "%s" % item.get('payload')
            if item.get('fmt') is not None:
                try:
                    text = item.get('fmt').format(**transform_data).encode('utf-8')
                    logging.debug("Message formmating successful: %s" % text)
                except Exception, e:
                    logging.debug("Message formatting failed: %s" % (str(e)))
                    pass
            item['message'] = text
        except:
            pass

        # If the formatmap for this topic has a function in it,
        # invoke that, pass data and replace message with its output
        if hasattr(item['fmt'], '__call__'):
            func = item['fmt']
            try:
                item['message'] = func(item['data'])
            except Exception, e:
                logging.debug("Cannot invoke %s(): %s" % (func, str(e)))

        st = Struct(**item)
        try:
            module = service_plugins[service]['module']
            module.plugin(srv, st)
        except Exception, e:
            logging.error("Cannot invoke plugin for `%s': %s" % (service, str(e)))

        q_in.task_done()

# http://code.davidjanes.com/blog/2008/11/27/how-to-dynamically-load-python-code/
def load_module(path):
    try:
        fp = open(path, 'rb')
        return imp.load_source(md(path).hexdigest(), path, fp)
    finally:
        try:
            fp.close()
        except:
            pass

def load_plugins(plugin_list, global_config):
    for p in plugin_list:
        filename = 'services/%s.py' % p

        service_plugins[p] = {}

        try:
            service_plugins[p]['module'] = load_module(filename)
            logging.debug("Plugin [%s] loaded" % (filename))
        except Exception, e:
            logging.error("Can't load %s plugin (%s): %s" % (p, filename, str(e)))
            sys.exit(1)

def connect():
    """
    Load service plugins, connect to the broker, launch daemon threads and listen forever
    """

    try:
        services = conf['services']
    except:
        logging.error("No services configured. Aborting")
        sys.exit(2)

    load_plugins(services, conf)

    srv.qttc = mqttc
    srv.logging = logging
    
    logging.debug("Attempting connection to MQTT broker %s:%d..." % (MQTT_HOST, MQTT_PORT))
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    # check for authentication
    if conf['username'] is not None:
        mqttc.username_pw_set(conf['username'], conf['password'])

    # configure the last-will-and-testament if set
    if MQTT_LWT is not None:
        mqttc.will_set(MQTT_LWT, payload=SCRIPTNAME, qos=0, retain=False)

    # Delays will be: 3, 6, 12, 24, 30, 30, ...
    # mqttc.reconnect_delay_set(delay=3, delay_max=30, exponential_backoff=True)

    try:
        result = mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
    except Exception, e:
        logging.error("Cannot connect to MQTT broker at %s:%d: %s" % (MQTT_HOST, MQTT_PORT, str(e)))
        sys.exit(2)

    # Launch worker threads to operate on queue
    for i in range(num_workers):
        t = threading.Thread(target=processor)
        t.daemon = True
        t.start()

    while True:
        try:
            mqttc.loop_forever()
        except socket.error:
            logging.info("MQTT server disconnected; sleeping")
            time.sleep(5)
        except:
            # FIXME: add logging with trace
            raise
         
def cleanup(signum, frame):
    """
    Signal handler to ensure we disconnect cleanly 
    in the event of a SIGTERM or SIGINT.
    """
    logging.debug("Disconnecting from MQTT broker...")
    mqttc.loop_stop()
    mqttc.disconnect()
    logging.info("Waiting for queue to drain")
    q_in.join()
    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)

if __name__ == '__main__':

    # use the signal module to handle signals
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
        
    # connect to broker and start listening
    connect()
