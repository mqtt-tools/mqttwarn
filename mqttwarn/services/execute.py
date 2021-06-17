# -*- coding: utf-8 -*-

__author__    = 'Tobias Brunner <tobias()tobru.ch>'
__copyright__ = 'Copyright 2016 Tobias Brunner'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import subprocess

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    config = item.config
    if type(config) == dict and 'text_replace' in config:
        replace = config['text_replace']
    else:
        replace = '[TEXT]'

    text = item.message
    cmd = [i.replace(replace, text) for i in item.addrs]

    try:
        res = subprocess.check_output(cmd, stdin=None, stderr=subprocess.STDOUT, shell=False, universal_newlines=True, cwd='/tmp')
    except Exception as e:
        srv.logging.warning("Cannot execute %s because %s" % (cmd, e))
        return False

    return True
