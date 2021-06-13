#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Vium https://github.com/Vium'
__copyright__ = 'Copyright 2016'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

# Based on the great SQLITE code by Jan-Piet Mens.

from builtins import str
import sqlite3
import unicodedata
from six import string_types


def plugin(srv, item):
    """ sqlite. Expects addrs to contain (path, tablename) """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    path  = item.addrs[0]
    table = item.addrs[1]
    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        srv.logging.warn("Cannot connect to sqlite at %s : %s" % (path, str(e)))
        return False

    table_cols =  {}
    #determine datatypes
    for key in item.data: #i.e. {"sensor_id":"testsensor","whatdata":"hello","data":1}"
        if key[0] == '_' or key == 'payload' or key == 'topic': #we just want to save the payload there is probably a better way
            continue
        else:
            if isinstance(item.data[key],  (int, float)):
                table_cols[key] = 'float'
                item.data[key] = str(item.data[key]) #make str for sql
            elif isinstance(item.data[key], string_types):
                table_cols[key] = 'varchar(20)'
                item.data[key] = "\'%s\'" % item.data[key] #add '' for sql

    # derive sql rudimentary definition string in case the table has to be created
    # i.e. 'key1 varchae(20), key2 varchar(20), key3 float'
    col_definition = ''
    for col in table_cols:
        col_definition = col_definition + col + ' ' + table_cols[col] +','
    col_definition = col_definition[:-1]
    col_definition= unicodedata.normalize('NFKD', col_definition).encode('ascii','ignore')

    #derive insert into string
    # i.e. 'key1, key2, key3'
    col_insert_into = ''
    for val in table_cols:
        col_insert_into  = col_insert_into + val + ','
    col_insert_into  = col_insert_into[:-1]
    col_insert_into= unicodedata.normalize('NFKD', col_insert_into).encode('ascii','ignore')

    #derive value string
    # i.e. '12, "hello", 23'
    col_values = ''
    for val in table_cols:
        col_values = col_values + item.data[val] + ','
    col_values = col_values[:-1]
    col_values= unicodedata.normalize('NFKD', col_values).encode('ascii','ignore')

    c = conn.cursor()
    try:
        srv.logging.debug("Inserting into SQLITE")
        c.execute('CREATE TABLE IF NOT EXISTS %s (%s);' % (table, col_definition))
    except Exception as e:
        srv.logging.warn("Cannot create sqlite table in %s : %s" % (path, str(e)))
        return False

    try:
        c.execute("INSERT INTO %s (%s) VALUES (%s);" % (table, col_insert_into, col_values))
        conn.commit()
        c.close()
        srv.logging.debug("Inserted into SQLITE")
    except Exception as e:
        srv.logging.warn("Cannot INSERT INTO sqlite:%s : %s" % (table, str(e)))

    return True
