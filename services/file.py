#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # item.config is brought in from the configuration file
    config   = item.config

    # addrs is a list[] associated with a particular target.
    # While it may contain more than one item (e.g. pushover)
    # the `file' service carries one only, i.e. a path name
    filename = item.addrs[0]

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    if type(config) == dict and 'append_newline' in config:
        text = text + "\n"

    try:
        f = open(filename, "a")
        f.write(text)
        f.close()
    except Exception, e:
        srv.logging.warning("Cannot write to file `%s': %s" % (filename, str(e)))
        return False

    return True
