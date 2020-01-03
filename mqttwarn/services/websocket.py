#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Giovanni Angoli <juzam76()gmail.com>'
__copyright__ = 'Copyright 2018 Giovanni Angoli'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

# This is basically the file.py service but declined for websockets, not more than s/file/websocket/g.

import websocket


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)


    # item.config is brought in from the configuration file
    config   = item.config

    # addrs is a list[] associated with a particular target.
    # While it may contain more than one item (e.g. pushover)
    # the `websocket' service carries one only, i.e. a ws:// or wss:// uri
    uri = item.addrs[0].format(**item.data).encode('utf-8')

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    try:
        ws = websocket.WebSocket()
        ws.connect(uri)
        ws.send(text)
        ws.close()
    except Exception as e:
        srv.logging.warning("Cannot write to websocket `%s': %s" % (uri, e))
        return False

    return True
