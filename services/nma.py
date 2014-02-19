#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_NMA=True
try:
    from pynma import PyNMA
except ImportError:
    HAVE_NMA=False


def plugin(srv, item):
    ''' expects (apikey, appname, eventname) in addrs'''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)
    if not HAVE_NMA:
        srv.logging.warn("PyNMA is not installed")
        return False

    try:
        apikey, appname, event = item.addrs
    except:
        srv.logging.warn("NMA incorrect # of target params passed")
        return False

    text = item.message
    priority = item.get('priority', 0)

    try:
        p = PyNMA()
        p.addkey(apikey)

        res = p.push(application=appname,
            event=event,
            description=text,
            url="",
            contenttype=None,
            priority=priority,
            batch_mode=False)

        srv.logging.debug("NMA returns %s" % (res))
        # {'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx': {'message': '', u'code': u'200', 'type': u'success', u'remaining': u'798', u'resettimer': u'46'}}

        # FIXME: test for code 200
    except Exception, e:
        srv.logging.warn("NMA failed: %s" % (str(e)))
        return False

    return True
