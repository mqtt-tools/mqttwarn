# -*- coding: utf-8 -*-
from six import string_types

__author__ = 'David Ventura'
__copyright__ = 'Copyright 2016 David Ventura'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import os
import json
import paramiko
from pipes import quote


def credentials(host, user=None, pwd=None, port=22):
    c = {}
    if user is None and pwd is None:
        config = paramiko.SSHConfig()
        p = os.path.expanduser('~') + '/.ssh/config'
        config.parse(open(p))
        o = config.lookup(host)

        ident = o['identityfile']
        if type(ident) is list:
            ident = ident[0]
        if 'port' not in o:
            o['port'] = port
        c = {'hostname': o['hostname'], 'port': int(o['port']), 'username': o['user'], 'key_filename': ident}
    else:
        c = {'hostname': host, 'port': port, 'username': user, 'password': pwd}

    return c


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)
    host = item.config["host"]
    port = 22
    user = None
    pwd = None

    if 'port' in item.config:
        port = item.config["port"]
    if 'user' in item.config:
        user = item.config["user"]
    if 'pass' in item.config:
        pwd = item.config["pass"]

    command = item.addrs[0]

    args = json.loads(item.payload)["args"]
    if type(args) is list and len(args) == 1:
        args = args[0]

    if isinstance(args, list):
        args = tuple([quote(v) for v in args])  # escape the shell args
    elif isinstance(args, string_types):
        args = (quote(args),)

    command = command % args

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        c = credentials(host, user=user, pwd=pwd, port=port)
        ssh.connect(**c)
        _, stdout, stderr = ssh.exec_command(command)

    except Exception as e:
        srv.logging.warning("Cannot run command '%s' on host '%s'" % (command, host))
        srv.logging.warning("%s" % e)
        return False

    return True
