#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
from pushover import pushover # https://github.com/pix0r/pushover
import ssl
import sys

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def on_message(mosq, userdata, msg):
    topic = msg.topic
    payload = str(msg.payload)

    for t in userdata['topicmap'].keys():
        if paho.topic_matches_sub(t, topic):
            appkey = userdata['topicmap'][t]
            try:
                pushover(message=payload,
                    user=userdata['userkey'], token=appkey)
            except Exception, e:
                print "Cannot pushover: %s" % str(e)
            break


def on_disconnect(mosq, userdata, rc):
    print "OOOOPS! disconnect"

cf = {}

try:
    execfile('config.py', cf)
except Exception, e:
    print "Cannot load config.py: %s" % str(e)
    sys.exit(2)

userdata = {
    'userkey' : cf['userkey'],
    'topicmap' : cf['topic_map'],
}

mqttc = paho.Client('mqtt2pushover', clean_session=True, userdata=userdata)
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect

if cf['username'] is not None:
    mqttc.username_pw_set(cf['username'], cf['password'])

mqttc.connect(cf['broker'], int(cf['port']), 60)

for topic in cf['topic_map'].keys():
    mqttc.subscribe(topic, 0)

try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    sys.exit(0)
except:
    raise
