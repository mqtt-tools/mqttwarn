#!/usr/bin/env python
# -*- coding: utf-8 -*-
from six import string_types

__author__    = 'Morten Høybye Frederiksen <morten()mfd-consult.dk>'
__copyright__ = 'Copyright 2016 Morten Høybye Frederiksen'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from builtins import str

import uuid
from iothub_client import *
from iothub_client_args import *


iothub_clients = {}


def iothub_connect(srv, item, deviceid, devicekey):
    # item.config is brought in from the configuration file
    try:
        hostname = item.config['hostname']
    except Exception as e:
        srv.logging.error("Incorrect target configuration for target=%s: %s", item.target, e)
        return False
    protocol = item.config.get('protocol', 'AMQP')
    timeout = item.config.get('timeout')
    minimum_polling_time = item.config.get('minimum_polling_time')
    message_timeout = item.config.get('message_timeout')

    # Prepare connection to Azure IoT Hub
    connection_string = "HostName=%s;DeviceId=%s;SharedAccessKey=%s" % (hostname, deviceid, devicekey)
    connection_string, protocol = get_iothub_opt(["-p", protocol], connection_string)
    client = IoTHubClient(connection_string, protocol)
    if client.protocol == IoTHubTransportProvider.HTTP:
        if timeout is not None:
            client.set_option("timeout", timeout)
        if minimum_polling_time is not None:
            client.set_option("MinimumPollingTime", minimum_polling_time)
    if message_timeout is not None:
        client.set_option("messageTimeout", message_timeout)
    srv.logging.info("Client: protocol=%s, hostname=%s, device=%s" % (protocol, hostname, deviceid))
    return client


def iothub_send_confirmation_callback(msg, res, srv):
    if res != IoTHubClientConfirmationResult.OK:
        srv.logging.error("Message confirmation: id=%s: %s", msg.message_id, res)
    else:
        srv.logging.debug("Message confirmation: id=%s: %s", msg.message_id, res)


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # addrs is a list[] containing device id and key.
    deviceid, devicekey = item.addrs

    # Create connection
    try:
        if not deviceid in iothub_clients:
            iothub_clients[deviceid] = iothub_connect(srv, item, deviceid, devicekey)
        client = iothub_clients[deviceid]
    except Exception as e:
        srv.logging.error("Unable to connect for target=%s, deviceid=%s: %s" % (item.target, deviceid, e))
        return False

    # Prepare message
    try:
        if isinstance(item.message, string_types):
            msg = IoTHubMessage(bytearray(item.message, 'utf8'))
        else:
            msg = IoTHubMessage(item.message)
        msg.message_id = str("%s:%s" % (item.target, uuid.uuid4().hex))
    except Exception as e:
        srv.logging.error("Unable to prepare message for target=%s: %s" % (item.target, str(e)))
        return False

    # Send
    try:
        client.send_event_async(msg, iothub_send_confirmation_callback, srv)
        srv.logging.debug("Message queued: id=%s", msg.message_id)
    except Exception as e:
        srv.logging.error("Unable to send to IoT Hub for target=%s: %s" % (item.target, str(e)))
        return False

    return True
