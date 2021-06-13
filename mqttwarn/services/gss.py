#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan Badenhorst <janhendrik.badenhorst()gmail.com>'
__copyright__ = 'Copyright 2014 Jan Badenhorst'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from builtins import str
try:
    import simplejson as json
except ImportError:
    import json

import gdata.spreadsheet.service


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

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
        for k, v in list(item.data.items()):
            row[k] = str(v)

        client.InsertRow(row, spreadsheet_key, worksheet_id)
        srv.logging.debug("Successfully added row to spreadsheet")

    except Exception as e:
        srv.logging.warn("Error adding row to spreadsheet %s [%s]: %s" % (spreadsheet_key, worksheet_id, e))
        return False

    return True
