#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Halacs <halacs87()gmail.com>'
__copyright__ = 'Copyright 2018 Halacs'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import MySQLdb


# https://mail.python.org/pipermail/tutor/2010-December/080701.html
def add_row(srv, cursor, tablename, rowdict):
    # XXX tablename not sanitized
    # XXX test for allowed keys is case-sensitive

    unknown_keys = None

    # filter out keys that are not column names
    cursor.execute("describe %s" % tablename)
    allowed_keys = set(row[0] for row in cursor.fetchall())
    keys = allowed_keys.intersection(rowdict)

    if len(rowdict) > len(keys):
        unknown_keys = set(rowdict) - allowed_keys

    columns = ", ".join(keys)
    values_template = ", ".join(["%s"] * len(keys))

    sql = "insert into %s (%s) values (%s)" % (tablename, columns, values_template)
    values = tuple(rowdict[key] for key in keys)
    cursor.execute(sql, values)

    return unknown_keys


def daraFv(srv, item, data, col_data, mapping):
    if data is not None:
        for key in list(data.keys()):
            if type(data[key]) is dict:
                daraFv(srv, item, data[key], col_data, mapping)
            else:
                if key in mapping:
                    try:
                        col_data[mapping[key]] = data[key].format(**data).encode('utf-8')
                    except Exception as e:
                        col_data[mapping[key]] = data[key]


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    host    = item.config.get('host', 'localhost')
    port    = item.config.get('port', 3306)
    user    = item.config.get('user')
    passwd  = item.config.get('pass')
    dbname  = item.config.get('dbname')

    try:
        table_name = item.addrs[0].format(**item.data).encode('utf-8')
        mapping = item.addrs[1]
        static = item.addrs[2]
    except:
        srv.logging.warn("halsql target incorrectly configured.")
        return False

    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname)
        cursor = conn.cursor()
    except Exception as e:
        srv.logging.warn("Cannot connect to mysql: %s" % e)
        return False

    col_data = {}

    # dynamic data part: remapp keys comes from the message
    daraFv(srv, item, item.data, col_data, mapping)
    
    # static data: add static key/value pairs to col_data
    if static is not None:
        col_data = dict(list(col_data.items()) + list(static.items()))

    try:
        unknown_keys = add_row(srv, cursor, table_name, col_data)
        if unknown_keys is not None:
            srv.logging.debug("Skipping unused keys %s" % ",".join(unknown_keys))
        conn.commit()
    except Exception as e:
        srv.logging.warn("Cannot add mysql row: %s" % e)
        cursor.close()
        conn.close()
        return False

    cursor.close()
    conn.close()

    return True

# vim: tabstop=4 expandtab
