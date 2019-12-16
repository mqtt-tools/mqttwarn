#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan Badenhorst <janhendrik.badenhorst()gmail.com>'
__copyright__ = 'Copyright 2014 Jan Badenhorst'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

try:
    import json
except ImportError:
    import simplejson as json

HAVE_GSS = True
try:
    import gdata.spreadsheet.service
except ImportError:
    HAVE_GSS = False


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)
    if not HAVE_GSS:
        srv.logging.warn("Google Spreadsheet is not installed")
        return False

    spreadsheet_key = item.addrs[0]
    worksheet_id = item.addrs[1]
    username = item.config['username']
    password = item.config['password']

    try:
        srv.logging.debug("Adding row to spreadsheet %s [%s]..." % (spreadsheet_key, worksheet_id))

        client = gdata.spreadsheet.service.SpreadsheetsService()
        client.debug = True
        client.email = username
        client.password = password
        client.source = 'mqttwarn'
        client.ProgrammaticLogin()

        # The API Does not like raw numbers as values.
        row = {}
        for k, v in item.data.items():
            row[k] = str(v)

        client.InsertRow(row, spreadsheet_key, worksheet_id)
        srv.logging.debug("Successfully added row to spreadsheet")

    except Exception as e:
        srv.logging.warn("Error adding row to spreadsheet %s [%s]: %s" % (spreadsheet_key, worksheet_id, str(e)))
        return False

    return True