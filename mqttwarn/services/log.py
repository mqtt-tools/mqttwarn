#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    level = item.addrs[0]

    text = item.message

    levels = {
        'debug': srv.logging.debug,
        'info': srv.logging.info,
        'warn': srv.logging.warning,
        'crit': srv.logging.critical,
        'error': srv.logging.error,
    }

    try:
        levels[level]("%s", text)
    except Exception as e:
        srv.logging.warn("Cannot invoke service log with level `%s': %s" % (level, e))
        return False

    return True
