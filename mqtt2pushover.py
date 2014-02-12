#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
from pushover import pushover # https://github.com/pix0r/pushover
import ssl
import sys
import logging

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def on_message(mosq, userdata, msg):
    topic = msg.topic
    payload = str(msg.payload)

    # Find the appkey for the particular topic of the message we just received

    for sub in userdata['topicmap'].keys():
        if paho.topic_matches_sub(sub, topic):
            rhs = userdata['topicmap'][sub]
            if type(rhs) is str:
                userkey = userdata['userkey']
                appkey = rhs
            else:
                userkey = rhs['userkey']
                appkey = rhs['appkey']

            # logging.debug("Using userkey=%s, appkey=%s" % (userkey, appkey))
            try:
                pushover(message=payload, user=userkey, token=appkey)
                logging.info("Posted [%s] to pushover from topic %s" % (str(payload), str(topic)))
            except Exception, e:
                logging.info("Cannot post to pushover: %s" % str(e))
            break


def on_disconnect(mosq, userdata, rc):
    print "OOOOPS! disconnected"

cf = {}

try:
    execfile('config.py', cf)
except Exception, e:
    print "Cannot load config.py: %s" % str(e)
    sys.exit(2)

LOGFILE = cf.get('logfile', 'logfile')
LOGFORMAT = '%(asctime)-15s %(message)s'
DEBUG=True

if DEBUG:
    logging.basicConfig(filename=LOGFILE, level=logging.DEBUG, format=LOGFORMAT)
else:
    logging.basicConfig(filename=LOGFILE, level=logging.INFO, format=LOGFORMAT)

logging.info("Starting")
logging.debug("DEBUG MODE")

userdata = {
    'userkey' : cf['userkey'],
    'topicmap' : cf['topicmap'],
}

mqttc = paho.Client('mqtt2pushover', clean_session=False, userdata=userdata)
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect

if cf['username'] is not None:
    mqttc.username_pw_set(cf['username'], cf['password'])

try:
    mqttc.connect(cf['broker'], int(cf['port']), 60)
except:
    logging.info("Can't connect to MQTT on %s:%d" % (cf['broker'], cf['port']))

for topic in cf['topicmap'].keys():
    logging.debug("Subscribing to %s" % topic)
    mqttc.subscribe(topic, 0)

try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    mqttc.loop_stop()
    mqttc.disconnect()
    sys.exit(0)
except:
    raise
