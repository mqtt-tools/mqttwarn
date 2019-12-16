#!/usr/bin/env python
# -*- coding: utf-8 -*-

#__originalauthor__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__author__    = 'Kuthullu Himself <kuthullu()gmail.com>'
__copyright__ = 'Copyright 2016 Kuthullu Himself'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_SQLITE=True
try:
    import sqlite3
except:
    HAVE_SQLITE=False

def plugin(srv, item):
    ''' sqlite. Expects addrs to contain (path, tablename) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    if HAVE_SQLITE is False:
        srv.logging.warn("Sqlite3 is not installed")
        return False

    path  = item.addrs[0]
    table = item.addrs[1]
    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        srv.logging.warn("Cannot connect to sqlite at %s : %s" % (path, str(e)))
        return False

    c = conn.cursor()
    try:
        c.execute('CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT, timestamp DATETIME NOT NULL)' % table)
    except Exception as e:
        srv.logging.warn("Cannot create sqlite table in %s : %s" % (path, str(e)))
        return False

    text = item.message

    try:
        c.execute('INSERT INTO %s VALUES (NULL, ?, datetime(\'now\'))' % table, (text, ))
        conn.commit()
        c.close()
    except Exception as e:
        srv.logging.warn("Cannot INSERT INTO sqlite:%s : %s" % (table, str(e)))

    return True
