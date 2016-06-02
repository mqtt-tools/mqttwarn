#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import paramiko

__author__    = 'David Ventura'
__copyright__ = 'Copyright 2016 David Ventura'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)
    host=item.config["host"]
    port=item.config["port"]
    user=item.config["user"]
    pwd=item.config["pass"]
    command=item.message

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host,port,user,pwd)
        _,stdout,stderr = ssh.exec_command(command)

        #for line in stdout:
        #    srv.logging.warning('... ' + line.strip('\n'))
	#Not really sure about what to do with output

    except Exception, e:
        srv.logging.warning("Cannot run command %s on host %s" % (command, host))

        return False

    return True

