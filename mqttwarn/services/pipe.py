#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import errno
import subprocess


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # addrs is a list[] with process name and args
    argv = item.addrs

    text = item.message

    if not text.endswith("\n"):
        text = text + "\n"

    try:
        proc = subprocess.Popen(argv,
            stdin=subprocess.PIPE, close_fds=True)
    except Exception as e:
        srv.logging.warn("Cannot create pipe: %s" % e)
        return False

    try:
        proc.stdin.write(text)
    except IOError as e:
        srv.logging.warn("Cannot write to pipe: errno %d" % (e.errno))
        return False
    except Exception as e:
        srv.logging.warn("Cannot write to pipe: %s" % e)
        return False

    proc.stdin.close()
    proc.wait()
    return True
