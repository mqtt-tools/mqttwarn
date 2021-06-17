# -*- coding: utf-8 -*-

__author__    = 'Andreas Motl <andreas.motl@panodata.org>'
__copyright__ = 'Copyright 2020 Andreas Motl'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

# https://github.com/caronc/apprise#developers
import apprise


def plugin(srv, item):
    """Send a message to Apprise plugin(s)."""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    addresses = item.addrs

    if not addresses:
        srv.logging.warning("Skipped sending notification to Apprise %s, "
                            "no addresses configured" % (item.target))
        return False

    sender = item.config.get('sender')
    sender_name = item.config.get('sender_name')
    baseuri = item.config['baseuri']
    title = item.title
    body = item.message

    try:
        srv.logging.debug("Sending notification to Apprise %s, addresses: %s" % (item.target, addresses))
        to = ','.join(addresses)

        # Create an Apprise instance.
        apobj = apprise.Apprise(asset=apprise.AppriseAsset(async_mode=False))

        # Add notification services by server url.
        uri = '{baseuri}?from={sender}&to={to}'.format(baseuri=baseuri, sender=sender, to=to)
        if sender_name:
            uri += '&name={sender_name}'.format(sender_name=sender_name)
        apobj.add(uri)

        # Submit notification.
        outcome = apobj.notify(
            body=body,
            title=title,
        )

        if outcome:
            srv.logging.info("Successfully sent message using Apprise")
            return True

        else:
            srv.logging.error("Sending message using Apprise failed")
            return False

    except Exception as e:
        srv.logging.error("Error sending message to %s: %s" % (item.target, e))
        return False
