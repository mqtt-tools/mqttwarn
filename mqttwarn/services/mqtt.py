#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from six import string_types
from future import standard_library
standard_library.install_aliases()

import configparser
import paho.mqtt.publish as mqtt


def conf(ini_file, params):
    try:
        c = configparser.ConfigParser()
        f = open(ini_file, 'r')
        c.readfp(f)
        f.close()
    except Exception as e:
        raise

    if c.has_section('defaults'):
        # differentiate bool, int, str
        if c.has_option('defaults', 'hostname'):
            params['hostname'] = c.get('defaults', 'hostname')
        if c.has_option('defaults', 'client_id'):
            params['client_id'] = c.get('defaults', 'client_id')
        if c.has_option('defaults', 'port'):
            params['port'] = c.getint('defaults', 'port')
        if c.has_option('defaults', 'qos'):
            params['qos'] = c.getint('defaults', 'qos')
        if c.has_option('defaults', 'retain'):
            params['retain'] = c.getboolean('defaults', 'retain')

    auth = None
    if c.has_section('auth'):
        auth = dict(c.items('auth'))

    tls = None
    if c.has_section('tls'):
        tls = dict(c.items('tls'))

    return dict(connparams=params, auth=auth, tls=tls)


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    config = item.config

    hostname = config.get('hostname', 'localhost')
    port = int(config.get('port', '1883'))
    qos = int(config.get('qos', 0))
    retain = int(config.get('retain', 0))
    username = config.get('username', None)
    password = config.get('password', None)

    params = {
        'hostname': hostname,
        'port': port,
        'qos': qos,
        'retain': retain,
        'client_id': None,
    }

    auth = None
    tls = None

    if username is not None:
        auth = {
            'username': username,
            'password': password
        }

    ini_file = None
    try:
        outgoing_topic, ini_file = item.addrs
    except:
        outgoing_topic = item.addrs[0]

    if ini_file is not None:
        try:
            data = conf(ini_file, params)
        except Exception as e:
            srv.logging.error("Target mqtt cannot load/parse INI file `%s': %s", ini_file, e)
            return False

        if 'connparams' in data and data['connparams'] is not None:
            params = dict(list(params.items()) + list(data['connparams'].items()))

    # Attempt to interpolate data into topic name. If it isn't possible
    # ignore, and return without publish

    if item.data is not None:
        try:
            outgoing_topic = item.addrs[0].format(**item.data).encode('utf-8')
        except:
            srv.logging.debug("Outgoing topic cannot be formatted; not published")
            return False

    outgoing_payload = item.message
    if isinstance(outgoing_payload, string_types):
        outgoing_payload = bytearray(outgoing_payload, encoding='utf-8')

    try:
        mqtt.single(outgoing_topic, outgoing_payload,
                    auth=auth,
                    tls=tls,
                    **params)
    except Exception as e:
        srv.logging.warning("Cannot PUBlish via `mqtt:%s': %s" % (item.target, e))
        return False

    return True
