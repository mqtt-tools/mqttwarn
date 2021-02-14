#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Tobias Brunner <tobias()tobru.ch>'
__copyright__ = 'Copyright 2016 Tobias Brunner / 2021 Joerg Gollnick'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import subprocess
import json
from pipes import quote
from six import string_types

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # same as for ssh - extract args from json item.message
    args=json.loads(item.message)["args"]

    if type(args) is list and len(args) == 1:
        args=args[0]

    if type(args) is list:
        args=tuple([ quote(v) for v  in args ]) #escape the shell args
    elif type(args) is str or type(args) is unicode:
        args=(quote(args),)

    topic=list(map( lambda x: quote(x), item.topic.split('/') ))
    outgoing_topic = item.addrs[0].format(full_topic=quote(item.topic),topic=topic)
    qos            = item.addrs[1]
    retain         = item.addrs[2]
    addrs          = item.addrs[3:]
    # replace args[0], args[1] ...
    cmd = [i.format(args=args) for i in addrs]
    srv.logging.debug("*** MODULE=%s: service=%s, command=%s outgoing_topic=%s", __file__, item.service, str( cmd ),outgoing_topic)

    try:
        res = subprocess.check_output(cmd, stdin=None, stderr=subprocess.STDOUT, shell=False, universal_newlines=True, cwd='/tmp')
    except Exception as e:
        srv.logging.warning("Cannot execute %s because %s" % (cmd, e))
        return False

    if outgoing_topic is not None:
        outgoing_payload = res.rstrip('\n')
        if isinstance(outgoing_payload, string_types):
            outgoing_payload = bytearray(outgoing_payload, encoding='utf-8')
        try:
            srv.mqttc.publish(outgoing_topic, outgoing_payload, qos=qos, retain=retain)
        except Exception as e:
            srv.logging.warning("Cannot PUBlish response %s: %s" % (outgoing_topic, e))
        return False

    return True
