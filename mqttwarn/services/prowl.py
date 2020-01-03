#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import prowlpy


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    apikey = item.addrs[0]
    application = item.addrs[1]

    title = item.get('title', srv.SCRIPTNAME)
    text = item.message
    priority = item.get('priority', 0)

    try:
        p = prowlpy.Prowl(apikey)
        p.post(application=title,
            event=application,
            description=text,
            priority=priority,
            providerkey=None,
            url=None)
    except Exception as e:
        srv.logging.warning("Cannot prowl: %s" % e)
        return False

    return True
