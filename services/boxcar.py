#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'David Cole <psyciknz()andc.nz>'
__copyright__ = 'Copyright 2017 David Cole'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import boxcar       # pip install python-boxcar
#from boxcar import Provider # pip install python-boxcar

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    
    #p.subscribe(email='test@example.com')
    #p.notify(emails=['test@example.com'],
    #     from_screen_name='test',
    #     message='This is a test message.',
    #     source_url='https://github.com/markcaudill/boxcar',
    #     icon_url='http://i.imgur.com/RC220wK.png')
    
    boxcar_keys = item.addrs
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s loading api", __file__, item.service, item.target)
    boxcar_api = boxcar.Provider(
        key                 = boxcar_keys[0]
    )
    #boxcar_api = boxcar.Provider(
    #    #key='vKLoSqB4vhQ4BPZ2TQ4z',
    #    key                 = boxcar_keys[0],
    #    #secret='hPiCqQMuRCDXbkVXYsq4zOu5AGZEZ0bGye7dfl5b'
    #    secret              = boxcar_keys[1]
    #)
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s loaded api: %s", __file__, item.service, item.target,boxcar_keys[0])
    
    text = item.message[0:138]
    try:
        srv.logging.debug("Sending notification to %s..." % (item.target))
        #boxcar_api.broadcast(from_screen_name=item.target,
        #    message=text,
        #    source_url='https://github.com/markcaudill/boxcar',
        #    icon_url='http://i.imgur.com/RC220wK.png')
        boxcar_api.notify(emails=['test@example.com'],
         from_screen_name=item.target,
         message=text,
         source_url='www.google.com',
         icon_url='http://i.imgur.com/RC220wK.png')
        
        srv.logging.debug("Successfully sent tweet")
    except Exception, e:
        srv.logging.error("BoxcarError: %s" % (str(e)))
        return False
    except Exception, e:
        srv.logging.error("Error sending tweet to %s: %s" % (item.target, str(e)))
        return False

    return True
