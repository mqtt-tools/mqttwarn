#!/usr/bin/env python
# -*- coding: utf-8 -*-
from six import string_types

__author__    = 'Morten Høybye Frederiksen <morten()mfd-consult.dk>'
__copyright__ = 'Copyright 2016-2020 Morten Høybye Frederiksen'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from builtins import str
import paho.mqtt.publish as mqtt
import paho.mqtt.client as mqttclient
import ssl

def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # addrs is a list[] containing device id and sas token
    deviceid, sastoken = item.addrs

    # iot hub name and qos is stored in config
    iothubname = item.config['iothubname']
    qos = int(item.config.get('qos', 0))
    if qos < 0 or qos > 1:
        srv.logging.error("Only QoS 0 or 1 allowed for Azure IoT Hub, not '%s'" % str(qos))
        return False

    # connection info...
    params = {
        'hostname': iothubname + ".azure-devices.net",
        'port': 8883,
        'protocol': mqttclient.MQTTv311,
        'qos': qos,
        'retain': False,
        'client_id': deviceid,
    }
    auth = {
        'username': iothubname + ".azure-devices.net/" +
            deviceid + "/?api-version=2018-06-30",
        'password': sastoken
    }
    tls = {
        'ca_certs': None,
        'certfile': None,
        'keyfile': None,
        'tls_version': ssl.PROTOCOL_TLSv1_2,
        'ciphers': None,
        'cert_reqs': ssl.CERT_NONE
    }

    # prepare topic
    d2c_topic = "devices/" + deviceid + "/messages/events/"

    # prepare payload
    try:
        if isinstance(item.message, string_types):
            payload = bytearray(item.message, 'utf8')
        else:
            payload = item.message
    except Exception as e:
        srv.logging.error("Unable to prepare message for target=%s: %s" % (item.target, str(e)))
        return False

    # publish...
    try:
        srv.logging.debug("Publishing to Azure IoT Hub for target=%s (%s): %s '%s'" % (item.target, deviceid, d2c_topic, str(payload)))
        mqtt.single(d2c_topic, payload, auth=auth, tls=tls, **params)
    except Exception as e:
        srv.logging.error("Unable to publish to Azure IoT Hub for target=%s (%s): %s" % (item.target, deviceid, str(e)))
        return False

    return True
