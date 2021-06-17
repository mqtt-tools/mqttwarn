#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import puka


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    uri = item.config['uri']

    exchange, routing_key = item.addrs

    try:
        srv.logging.debug("AMQP publish to %s [%s/%s]..." % (item.target, exchange, routing_key))

        client = puka.Client(uri)
        promise = client.connect()
        client.wait(promise)

        headers = {
            'content_type': 'text/plain',
            'x-agent': 'mqttwarn',
            'delivery_mode': 1,
        }
        promise = client.basic_publish(exchange=exchange,
                                       routing_key=routing_key,
                                       headers=headers,
                                       body=item.message)
        client.wait(promise)
        client.close()

        srv.logging.debug("Successfully published AMQP notification")
    except Exception as e:
        srv.logging.warning("Error on AMQP publish to %s [%s/%s]: %s" % (item.target, exchange, routing_key, e))
        return False

    return True
