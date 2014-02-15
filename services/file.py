#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: targets=%s, addrs=%s", __file__, item.targets, item.addrs)

    topic    = item.topic
    payload  = item.payload
    addrs    = item.addrs
    targets  = item.targets
    title    = item.title
    priority = item.priority
    fmt      = item.fmt
    config   = item.config
    message  = item.message     # possibly converted payload

    filename = addrs[0]

    text = message
    if message is None:
        text = payload

    print "M=", message
    print "P=", payload

    try:
        f = open(filename, "a")
        f.write(text)
        f.close()
    except Exception, e:
        srv.logging.warning("Cannot write to file `%s': %s" % (filename, str(e)))

    return  
