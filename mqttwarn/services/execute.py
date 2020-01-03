#!/usr/bin/env python2
# -*- coding: utf-8 -*-

__author__    = 'Tobias Brunner <tobias()tobru.ch>'
__copyright__ = 'Copyright 2016 Tobias Brunner'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import subprocess
import json
from pipes import quote

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # same as for ssh
    args=json.loads(item.message)["args"]

    if type(args) is list and len(args) == 1:
        args=args[0]


    if type(args) is list:
        args=tuple([ quote(v) for v  in args ]) #escape the shell args
    elif type(args) is str or type(args) is unicode:
        args=(quote(args),)

    cmd = [i.format(args=args) for i in item.addrs]
    srv.logging.debug("*** MODULE=%s: service=%s, command=%s", __file__, item.service, str( cmd ))

    try:
        res = subprocess.check_output(cmd, stdin=None, stderr=subprocess.STDOUT, shell=False, universal_newlines=True, cwd='/tmp')
    except Exception as e:
        srv.logging.warning("Cannot execute %s because %s" % (cmd, e))
        return False

    return True
