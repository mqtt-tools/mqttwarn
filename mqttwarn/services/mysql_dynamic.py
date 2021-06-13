#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'João Paulo Barraca <jpbarraca()gmail.com>'
__copyright__ = 'Copyright 2014 João Paulo Barraca'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

# Credits to Jan-Piet Mens for the mysql.py code which served as basis for this module

from six import string_types
from builtins import str

import re
import time
import traceback
import MySQLdb


def add_row(srv, cursor, index_table_name, table_name, rowdict, ignorekeys):
    keys = []
    clean_key = re.compile(r'[^\d\w_-]+')
    for k, v in list(rowdict.items()):
        if k in ignorekeys:
            continue

        key = clean_key.sub('', k)
        keys.append({'ori': k, 'clean': key})

    try:
        cursor.execute("describe %s" % table_name)
    except Exception as e:
        colspec = ['`id` INT AUTO_INCREMENT']
        for k in keys:
            if isinstance(rowdict[k['ori']], int):
                colspec.append('`%s` LONG' % k['clean'])
            elif isinstance(rowdict[k['ori']], (float)):
                colspec.append('`%s` FLOAT' % k['clean'])
            else:
                colspec.append('`%s` TEXT' % k['clean'])

        query = 'create table `%s` (' % table_name
        query += ','.join(colspec)
        query += ', PRIMARY KEY ID(`id`)) CHARSET=utf8'

        try:
            cursor.execute(query)
        except Exception as e:
            srv.logging.warn("Mysql target incorrectly configured. Could not create table %s: %s" % table_name, e)
            return False
    try:
        columns = ''
        values_template = ''
        sql = ''
        values = tuple()

        for i in range(len(keys)):
            if i > 0:
                columns += ","
                values_template += ","

            columns += " " + keys[i]['clean']
            values_template += " %s"
            values += (MySQLdb.escape_string(str(rowdict[keys[i]['ori']])),)

        sql = "insert into %s (%s) values (%s)" % (table_name, columns, values_template)

        cursor.execute(sql, values)
    except Exception as e:
        srv.logging.warn("Could not insert value into table %s. Query: %s, values: %s, Error: %s" % \
                         (table_name, sql, values, e))
        return False

    try:
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        query = 'insert into %s set topic="%s", ts="%s" on duplicate key update ts="%s"' % \
                (index_table_name, table_name, now, now)
        cursor.execute(query)
    except Exception as e:
        srv.logging.warn("Could not insert value into index table %s" % \
                         index_table_name)

    return True


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s target=%s", __file__, item.service, item.target)

    host = item.config.get('host', 'localhost')
    port = item.config.get('port', 3306)
    user = item.config.get('user')
    passwd = item.config.get('pass')
    dbname = item.config.get('dbname')
    index_table_name = item.config.get('index')
    # ignore_keys = item.config.get('ignore_')

    # Sanitize table_name
    table_name = item.data['topic'].replace('/', '_')
    table_name = re.compile(r'[^\d\w_]+').sub('', table_name)

    try:
        conn = MySQLdb.connect(host=host,
                               user=user,
                               passwd=passwd,
                               db=dbname,
                               port=port)
        cursor = conn.cursor()
    except Exception as e:
        srv.logging.warn("Cannot connect to mysql: %s" % e)
        return False

    # Create new dict for column data. First add fallback column
    # with full payload. Then attempt to use formatted JSON values
    col_data = {}

    if item.data is not None:
        for key in list(item.data.keys()):
            try:
                if isinstance(col_data[key], string_types):
                    col_data[key] = item.data[key].format(**item.data).encode('utf-8')
            except Exception as e:
                col_data[key] = item.data[key]
    try:
        result = add_row(srv, cursor, index_table_name, table_name, col_data, item.addrs)
        if not result:
            srv.logging.debug("Failed building values to add to database")
        else:
            conn.commit()
    except Exception as e:
        srv.logging.warn("Cannot add mysql row: %s" % e)
        traceback.print_exc()
        cursor.close()
        conn.close()
        return False

    cursor.close()
    conn.close()

    return True
