#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on the mysql.py service by Jan-Piet Mens

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>, Martyn Whitwell <martyn.whitwell()gmail.com>'
__copyright__ = 'Copyright 2016 Jan-Piet Mens,  Martyn Whitwell'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'


# example configuration in mqttwarn.ini:
# [config:postgres]
# host    = 'localhost'
# user    = 'username'
# pass    = 'password'
# dbname  = 'databasename'
# targets = { 
#    'target1': ['table1', 'fallbackcol1', 'schema']
#  }


import psycopg2


def add_row(cursor, tablename, rowdict, schema):
    # XXX tablename not sanitized
    # XXX test for allowed keys is case-sensitive

    unknown_keys = None

    # filter out keys that are not column names
    cursor.execute(
        "SELECT column_name \
        FROM INFORMATION_SCHEMA.COLUMNS \
        where table_schema = '%s' AND table_name = '%s'" % (
        schema, tablename))
    allowed_keys = set(row[0] for row in cursor.fetchall())
    keys = allowed_keys.intersection(rowdict)

    if len(rowdict) > len(keys):
        unknown_keys = set(rowdict) - allowed_keys

    columns = ", ".join(keys)
    values_template = ", ".join(["%s"] * len(keys))

    sql = "insert into %s.%s (%s) values (%s)" % (
        schema, tablename, columns, values_template)
    values = tuple(rowdict[key] for key in keys)
    cursor.execute(sql, values)

    return unknown_keys


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    host    = item.config.get('host', 'localhost')
    port    = item.config.get('port', 5432)
    user    = item.config.get('user')
    passwd  = item.config.get('pass')
    dbname  = item.config.get('dbname')

    try:
        table_name = item.addrs[0].format(**item.data).encode('utf-8')
        fallback_col = item.addrs[1].format(**item.data).encode('utf-8')
        try:
            schema = item.addrs[2].format(**item.data).encode('utf-8')
        except:
            schema = 'public'
    except:        
        srv.logging.warn("postgres target incorrectly configured")
        return False

    try:
        conn = psycopg2.connect(host=host,
                    port=port,
                    user=user,
                    password=passwd,
                    database=dbname)
        cursor = conn.cursor()
    except Exception as e:
        srv.logging.warn("Cannot connect to postgres: %s" % e)
        return False

    text = item.message

    # Create new dict for column data. First add fallback column
    # with full payload. Then attempt to use formatted JSON values
    col_data = {
        fallback_col : text
       }

    if item.data is not None:
        for key in list(item.data.keys()):
            try:
                col_data[key] = item.data[key].format(**item.data).encode('utf-8')
            except Exception as e:
                col_data[key] = item.data[key]

    try:
        unknown_keys = add_row(cursor, table_name, col_data, schema)
        if unknown_keys is not None:
            srv.logging.debug("Skipping unused keys %s" % ",".join(unknown_keys))
        conn.commit()
    except Exception as e:
        srv.logging.warn("Cannot add postgres row: %s" % e)
        cursor.close()
        conn.close()
        return False

    cursor.close()
    conn.close()

    return True
