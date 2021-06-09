#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014-2021 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import pyprowl


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    apikey = item.addrs[0]
    application = item.addrs[1]

    title = item.get('title', srv.SCRIPTNAME)
    text = item.message
    priority = int(item.get('priority', 0))

    try:
        p = pyprowl.Prowl(apikey)
        p.verify_key()
        srv.logging.info("Prowl API key successfully verified")
    except Exception as e:
        srv.logging.error("Error verifying Prowl API key: {}".format(e))
        return False

    try:
        p.notify(event=title, description=text,
                 priority=priority, url=None,
                 appName=application)
        srv.logging.debug("Sending notification to Prowl succeeded")
    except Exception as e:
        srv.logging.warning("Sending notification to Prowl failed: %s" % e)
        return False

    return True
