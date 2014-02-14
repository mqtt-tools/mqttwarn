#!/usr/bin/env python

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: targets=%s, addrs=%s", __file__, item.targets, item.addrs)

    topic    = item.topic
    payload  = item.payload
    addrs    = item.addrs
    targets  = item.targets
    title    = item.title
    priority = item.priority
    fmt      = item.fmt
    config   = item.config

    filename = addrs[0]

    text = "%s\n" % payload
    if fmt is not None:
        try:
            # text = fmt.format(**item).encode('utf-8')
            text = fmt.format(**(item.enum()))
        except:
            text = "%s\n" % payload

    try:
        f = open(filename, "a")
        f.write(text)
        f.close()
    except Exception, e:
        srv.logging.warning("Cannot write to file `%s': %s" % (filename, str(e)))

    return  
