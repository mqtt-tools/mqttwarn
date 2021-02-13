#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example "agent" for Zabbix/mqttwarn which publishes two metrics
# every few seconds.

import paho.mqtt.client as paho   # pip install paho-mqtt
import ssl
import time
import sys
from random import randint

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

CLIENT = 'jog09'
HOST_TOPIC = "zabbix/clients/%s" % CLIENT

mqttc = paho.Client(clean_session=True, userdata=None)

def metric(name, value):
    mqttc.publish("zabbix/item/%s/%s" % (CLIENT, name), value)
    mqttc.loop()

mqttc.tls_set('/Users/jpm/tmp/mqtt/root.ca',
    tls_version=ssl.PROTOCOL_TLSv1)

mqttc.tls_insecure_set(True)    # Ensure False in production

# If this client dies, ensure broker publishes our death on our behalf (LWT)
mqttc.will_set(HOST_TOPIC, payload="0", qos=0, retain=True)

# mqttc.username_pw_set('john', 'secret')
mqttc.connect("localhost", 8883, 60)

# Indicate host is up
mqttc.publish(HOST_TOPIC, "1")
rc = 0
while rc == 0:
    try:
        rc = mqttc.loop()

        metric('system.cpu.load', randint(2, 8))
        metric('time.stamp',  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        time.sleep(10)
    except KeyboardInterrupt:
        sys.exit(0)
