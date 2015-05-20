#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rrdtool

__author__    = 'devsaurus <devsaurus@users.noreply.github.com>'
__copyright__ = 'Copyright 2015'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    try:
        # addrs is a list[] associated with a particular target.
        # it can contain an arbitrary amount of entries that are just
        # passed along to rrdtool
        rrdtool.update(item.addrs, "N:" + text)
    except Exception, e:
        srv.logging.warning("Cannot call rrdtool")
        return False

    return True
