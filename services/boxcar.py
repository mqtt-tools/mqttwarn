#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'David Cole <psyciknz()andc.nz>'
__copyright__ = 'Copyright 2017 David Cole'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import boxcar       # pip install python-boxcar
from httplib import HTTPSConnection, HTTPException
import ssl
import urllib
from urllib import urlencode
#from boxcar import Provider # pip install python-boxcar

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # Prepare the notification parameters
    
    boxcar_keys = item.addrs
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s loading api", __file__, item.service, item.target)
    
    srv.logging.debug('starting')
    srv.logging.debug(boxcar_keys)
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s loaded api: %s", __file__, item.service, item.target,boxcar_keys[0])
    
    text = item.message[0:138]
    try:
        srv.logging.debug("Sending notification to %s..." % (item.target))
        #boxcar_api.broadcast(from_screen_name=item.target,
        #    message=text,
        #    source_url='https://github.com/markcaudill/boxcar',
        #    icon_url='http://i.imgur.com/RC220wK.png')
        #boxcar_api.notify(emails=['test@example.com'],
        # from_screen_name=item.target,
        # message=text,
        # source_url='www.google.com',
        # icon_url='http://i.imgur.com/RC220wK.png')
        
        params = urlencode(
            {
  	        'user_credentials': boxcar_keys[0],
            'notification[title]': item.target,
            'notification[source_name]': item.target,
            'notification[icon_url]' : boxcar_keys[1],

            'notification[long_message]': text,
            'notification[sound]': boxcar_keys[2]
            }
        )
  
        # Create a secure connection to Boxcar and POST the message
        context = ssl.create_default_context()
        conn = HTTPSConnection('new.boxcar.io', context=context)
        conn.request('POST', '/api/notifications', params)
  
        # Check the response
        response = conn.getresponse()
        srv.logging.debug("Boxcar result: %s: %s" % (response.status, response.reason))
        data = response.read()
        srv.logging.debug(data)
  
        # Clean up the connection
        conn.close()

        srv.logging.debug("Successfully sent tweet")
    except Exception, e:
        srv.logging.error("BoxcarError: %s" % (str(e)))
        return False
    except Exception, e:
        srv.logging.error("Error sending tweet to %s: %s" % (item.target, str(e)))
        return False

    return True
