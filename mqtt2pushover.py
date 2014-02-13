#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pushover import pushover     # https://github.com/pix0r/pushover
import paho.mqtt.client as paho   # pip install paho-mqtt
import logging
import signal
import sys
import time

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>, Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

# load configuration
conf = {}
try:
    execfile('/etc/mqtt2pushover/mqtt2pushover.conf', conf)
except IOError:
    execfile('mqtt2pushover.conf', conf)
except Exception, e:
    print "Cannot load /etc/mqtt2pushover/mqtt2pushover.conf: %s" % str(e)
    sys.exit(2)

LOGFILE = conf['logfile']
LOGLEVEL = conf['loglevel']
LOGFORMAT = conf['logformat']

MQTT_HOST = conf['broker']
MQTT_PORT = int(conf['port'])
MQTT_LWT = conf['lwt']

# initialise logging    
logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
logging.info("Starting mqtt2pushover")
logging.info("INFO MODE")
logging.debug("DEBUG MODE")

# initialise MQTT broker connection
mqttc = paho.Client('mqtt2pushover', clean_session=False)

# check for authentication
if conf['username'] is not None:
    mqttc.username_pw_set(conf['username'], conf['password'])

# configure the last-will-and-testament
mqttc.will_set(MQTT_LWT, payload="mqtt2pushover", qos=0, retain=False)

def connect():
    """
    Connect to the broker
    """
    logging.debug("Attempting connection to MQTT broker %s:%d..." % (MQTT_HOST, MQTT_PORT))
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    result = mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
    if result == 0:
        mqttc.loop_forever()
    else:
        logging.info("Connection failed with error code %s. Retrying in 10s...", result)
        time.sleep(10)
        connect()
         
def disconnect(signum, frame):
    """
    Signal handler to ensure we disconnect cleanly 
    in the event of a SIGTERM or SIGINT.
    """
    logging.debug("Disconnecting from MQTT broker...")
    mqttc.loop_stop()
    mqttc.disconnect()
    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)

def on_connect(mosq, userdata, result_code):
    logging.debug("Connected to MQTT broker, subscribing to topics...")
    for topic in conf['topicuser'].keys():
        logging.debug("Subscribing to %s" % topic)
        mqttc.subscribe(topic, 0)

def on_message(mosq, userdata, msg):
    """
    Message received from the broker
    """
    topic = msg.topic
    payload = str(msg.payload)
    logging.debug("Message received on %s: %s" % (topic, payload))
    
    users = None
    title = "Info"
    priority = "-1"

    # Try to find matching settings for this topic
    for sub in conf['topicuser']:
        if paho.topic_matches_sub(sub, topic):
            try:
                users = conf['topicuser'][sub]
                title = conf['topictitle'][sub]
                priority = conf['topicpriority'][sub]
            except:
                pass
            break

    for user in users:
        logging.debug("Sending pushover notification to %s [%s, %s]..." % (user, title, priority))
        userkey = conf['pushoveruser'][user][0]
        appkey = conf['pushoveruser'][user][1]
        try:
            pushover(
                message=payload, 
                user=userkey, token=appkey, 
                title=title, priority=priority,
                retry=60, expire=3600)
            logging.debug("Successfully sent notification")
        except Exception, e:
            logging.warn("Notification failed: %s" % str(e))

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

# use the signal module to handle signals
signal.signal(signal.SIGTERM, disconnect)
signal.signal(signal.SIGINT, disconnect)
        
# connect to broker and start listening
connect()
