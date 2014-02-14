#!/usr/bin/env python

def plugin(srv, item):

    srv.logging.debug("*** SMTP ")
    srv.logging.debug("SMTP-targets = %s" % item['targets'])
    srv.logging.debug("SMTP-addrs  = %s" % item['addrs'] )
    srv.logging.debug("SMTP-config  = %s" % item['config'] )

    return  
