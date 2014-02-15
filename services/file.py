#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    config   = item.config


# FIXME: remove next line
    print item.data

    filename = item.addrs[0]

    text = item.get('message', item.payload)
    if type(config) == dict and 'append_newline' in config:
        text = text + "\n"

    try:
        f = open(filename, "a")
        f.write(text)
        f.close()
    except Exception, e:
        srv.logging.warning("Cannot write to file `%s': %s" % (filename, str(e)))

    return  
