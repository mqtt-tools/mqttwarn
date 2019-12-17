#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'devsaurus <devsaurus@users.noreply.github.com>'
__copyright__ = 'Copyright 2015'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import re
import rrdtool


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    try:
        # addrs is a list[] associated with a particular target.
        # it can contain an arbitrary amount of entries that are just
        # passed along to rrdtool
        # mofified by otfdr @ github to accept abitray arguments with
        # the payload and to not always add the 'N' in front
        # 2017-06-05 - fix/enhancement for https://github.com/jpmens/mqttwarn/issues/248
        if re.match( "^\d+$", text ):
                rrdtool.update(item.addrs, "N:" + text)
        else:
                rrdtool.update(item.addrs + text.split())
    except Exception as e:
        srv.logging.warning("Cannot call rrdtool")
        return False

    return True
