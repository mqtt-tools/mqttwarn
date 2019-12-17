#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import subprocess


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    voice = item.addrs[0]
    text = item.message

    argv = [ "/usr/bin/say", "-f", "-", "--voice=%s" % voice ]

    try:
        proc = subprocess.Popen(argv,
            stdin=subprocess.PIPE, close_fds=True)
    except Exception as e:
        srv.logging.warn("Cannot create osxsay pipe: %s" % e)
        return False

    try:
        proc.stdin.write(text)
    except IOError as e:
        srv.logging.warn("Cannot write to osxsay pipe: errno %d" % (e.errno))
        return False
    except Exception as e:
        srv.logging.warn("Cannot write to osxsay pipe: %s" % e)
        return False

    proc.stdin.close()
    proc.wait()
    return True
