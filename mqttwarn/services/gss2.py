#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Philipp Adelt <autosort-github@philipp.adelt.net>, based on code by Jan Badenhorst'
__copyright__ = 'Copyright 2016 Philipp Adelt, 2014 Jan Badenhorst'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import os

try:
    import simplejson as json
except ImportError:
    import json

import gspread
import oauth2client.client
import oauth2client.file
from oauth2client import clientsecrets


SCOPE = "https://spreadsheets.google.com/feeds"


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        spreadsheet_url = item.addrs[0]
        worksheet_name = item.addrs[1]
        client_secrets_filename = item.config['client_secrets_filename']
        oauth2_code = item.config['oauth2_code']
        oauth2_storage_filename = item.config['oauth2_storage_filename']
    except KeyError as e:
        srv.logging.error("Some configuration item is missing: %s" % e)
        return False

    if not os.path.exists(client_secrets_filename):
        srv.logging.error("Cannot find file '%s'." % client_secrets_filename)
        return False

    try:
        srv.logging.debug("Adding row to spreadsheet %s [%s]..." % (spreadsheet_url, worksheet_name))
        if os.path.isfile(oauth2_storage_filename):
            # Valid credentials from previously completed authentication?
            srv.logging.debug("Trying to use credentials from file '%s'." %
                oauth2_storage_filename)
            storage = oauth2client.file.Storage(oauth2_storage_filename)
            credentials = storage.get()
            if credentials is None or credentials.invalid:
                srv.logging.error("Error reading credentials from file '%s'." %
                    oauth2_storage_filename)
                return False
        elif oauth2_code is not None and len(oauth2_code) > 0:
            # After restart - hopefully with the code coming from the Google webpage.
            srv.logging.debug("Trying to use client_secrets from '%s' and OAuth code '%s'." %
                (client_secrets_filename, oauth2_code))
            try:
                credentials = oauth2client.client.credentials_from_clientsecrets_and_code(
                    client_secrets_filename,
                    scope=SCOPE,
                    code=oauth2_code,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob')
                if credentials is None:
                    raise clientsecrets.InvalidClientSecretsError("Resulting credentials are None!?")
            except clientsecrets.InvalidClientSecretsError as e:
                srv.logging.error("Something went wrong using '%s' and OAuth code '%s': %s" %
                    (client_secrets_filename, oauth2_code, e))
                return False
            except oauth2client.client.FlowExchangeError as e:
                if 'invalid_grantCode' in e.message:
                    srv.logging.error("It seems you need to start over: Clear the "
                        "'oauth2_code'-field and restart mqttwarn.")
                    return False
                else:
                    raise e

            # Store credentials for next event.
            storage = oauth2client.file.Storage(oauth2_storage_filename)
            storage.put(credentials)

        else:
            # Start a new authentication flow and scream the URL to visit to the logs.
            flow = oauth2client.client.flow_from_clientsecrets(
                client_secrets_filename,
                scope=SCOPE,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            auth_uri = flow.step1_get_authorize_url()
            srv.logging.error('NO AUTHENTICATION AVAILABLE: Visit this URL and copy code to '
                'mqttwarn.ini -> config:gss2 -> oauth2_code: %s' % auth_uri)
            return False

        gc = gspread.authorize(credentials)
        wks = gc.open_by_url(spreadsheet_url).worksheet(worksheet_name)
        col_names = wks.row_values(1)

        # Column names found need to be keys in item.data to end up in the new row.
        values = []
        for col in col_names:
            values.append(item.data.get(col, ""))

        wks.append_row(values)

        srv.logging.debug("Successfully added row to spreadsheet")

    except Exception as e:
        srv.logging.warn("Error adding row to spreadsheet %s [%s]: %s" % (spreadsheet_url, worksheet_name, e))
        return False

    return True
