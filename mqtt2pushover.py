#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pushover import pushover # https://github.com/pix0r/pushover

import paho.mqtt.client as paho   # pip install paho-mqtt
import logging
import sys, time

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>, Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def on_connect(mosq, userdata, rc):
    logging = userdata['logging']
    logging.debug("Connected to MQTT broker")
    for topic in userdata['topickey'].keys():
        mqttc.subscribe(topic, 0)

def on_message(mosq, userdata, msg):
    topic = msg.topic
    payload = str(msg.payload)

    logging = userdata['logging']
    logging.debug("Message received on %s: %s" % (topic, payload))

    recipients = userdata['topickey'][topic]
    title = userdata['topictitle'][topic]
    priority = userdata['topicpriority'][topic]

    for recipient in recipients:
        userkey = userdata['pushoverkey'][recipient][0]
        appkey = userdata['pushoverkey'][recipient][1]

        logging.debug("Sending notification to %s..." % recipient)
        try:
            pushover(message=payload,
                user=userkey, token=appkey,
                title=title, priority=priority,
                retry=60, expire=3600)
            logging.debug("Successfully sent notification")
        except Exception, e:
            logging.warn("Notification failed: %s" % str(e))

def on_disconnect(mosq, userdata, rc):
    logging = userdata['logging']
    logging.debug("Connection to MQTT broker lost")
    time.sleep(10)

if __name__ == '__main__':

    # load configuration
    conf = {}
    try:
        execfile('mqtt2pushover.conf', conf)
    except Exception, e:
        print "Cannot load mqtt2pushover.conf: %s" % str(e)
        sys.exit(2)

    # initialise logging    
    logfile = conf['logfile']
    loglevel = conf['loglevel']
    logformat = '%(asctime)-15s %(message)s'

    logging.basicConfig(filename=logfile, level=loglevel, format=logformat)
    logging.info("mqtt2pushover started")
    logging.debug("DEBUG MODE")

    # create the user data to pass through to our MQTT listeneres
    userdata = {
        'logging'       : logging,
        'pushoverkey'   : conf['pushoverkey'],
        'topickey'      : conf['topickey'],
        'topictitle'    : conf['topictitle'],
        'topicpriority' : conf['topicpriority'],
    }

    # initialise the MQTT broker connection
    mqttc = paho.Client('mqtt2pushover', clean_session=False, userdata=userdata)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    # check for authentication
    username = conf['username']
    if username is not None:
        password = conf['password']
        mqttc.username_pw_set(username, password)

    # configure the last-will-and-testament
    lwt = conf['lwt']
    mqttc.will_set(lwt, payload="mqtt2pushover", qos=0, retain=False)

    # attempt to connect to the MQTT broker
    broker = conf['broker']
    port = int(conf['port'])
    try:
        mqttc.connect(broker, port, 60)
    except Exception, e:
        logging.error("Failed to connect to MQTT broker on %s:%d: %s" % (broker, port, str(e)))
        sys.exit(2)

    # start listening...
    try:
        mqttc.loop_forever()
    except KeyboardInterrupt:
        mqttc.loop_stop()
        mqttc.disconnect()
        sys.exit(0)
    except Exception, e:
        logging.error("Error on MQTT broker connection: %s" % str(e))
        sys.exit(2)
