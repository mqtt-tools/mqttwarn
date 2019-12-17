#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Fabian Affolter <fabian()affolter-engineering.ch>'
__copyright__ = 'Copyright 2014 Fabian Affolter'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import syslog


def plugin(srv, item):
    """Transfer a message to a syslog server."""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s",
                        __file__, item.service, item.target)

    facilities = {
        'kernel' : syslog.LOG_KERN,
        'user'   : syslog.LOG_USER,
        'mail'   : syslog.LOG_MAIL,
        'daemon' : syslog.LOG_DAEMON,
        'auth'   : syslog.LOG_KERN,
        'LPR'    : syslog.LOG_LPR,
        'news'   : syslog.LOG_NEWS,
        'uucp'   : syslog.LOG_UUCP,
        'cron'   : syslog.LOG_CRON,
        'syslog' : syslog.LOG_SYSLOG,
        'local0' : syslog.LOG_LOCAL0,
        'local1' : syslog.LOG_LOCAL1,
        'local2' : syslog.LOG_LOCAL2,
        'local3' : syslog.LOG_LOCAL3,
        'local4' : syslog.LOG_LOCAL4,
        'local5' : syslog.LOG_LOCAL5,
        'local6' : syslog.LOG_LOCAL6,
        'local7' : syslog.LOG_LOCAL7
    }

    options = {
        'pid'    : syslog.LOG_PID,
        'cons'   : syslog.LOG_CONS,
        'ndelay' : syslog.LOG_NDELAY,
        'nowait' : syslog.LOG_NOWAIT,
        'perror' : syslog.LOG_PERROR
    }

    priorities = {
        5        : syslog.LOG_EMERG,
        4        : syslog.LOG_ALERT,
        3        : syslog.LOG_CRIT,
        2        : syslog.LOG_ERR,
        1        : syslog.LOG_WARNING,
        0        : syslog.LOG_NOTICE,
        -1       : syslog.LOG_INFO,
        -2       : syslog.LOG_DEBUG
    }

    title = item.get('title', srv.SCRIPTNAME)
    facility  = facilities[item.addrs[0]]
    option = options[item.addrs[1]]

    priority = priorities[item.get('priority', -1)]
    message = item.message

    try:
        srv.logging.debug("Message is going to syslog facility %s..." \
            % ((item.target).upper()))
        syslog.openlog(title, option, facility)
        syslog.syslog(priority, message)
        srv.logging.debug("Successfully sent")
        syslog.closelog()
    except Exception as e:
        srv.logging.error("Error sending to syslog: %s" % e)
        syslog.closelog()
        return False

    return True
