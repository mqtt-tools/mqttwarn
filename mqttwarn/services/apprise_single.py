# -*- coding: utf-8 -*-

__author__    = 'Andreas Motl <andreas.motl@panodata.org>'
__copyright__ = 'Copyright 2020-2021 Andreas Motl'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

# https://github.com/caronc/apprise#developers
from collections import OrderedDict

import apprise

from mqttwarn.services.apprise_util import obtain_apprise_arguments, add_url_params, get_all_template_argument_names

APPRISE_ALL_ARGUMENT_NAMES = get_all_template_argument_names()


def plugin(srv, item):
    """Send a message to a single Apprise plugin."""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    sender = item.config.get('sender')
    sender_name = item.config.get('sender_name')
    baseuri = item.config['baseuri']
    addresses = item.addrs
    title = item.title
    body = item.message

    try:
        srv.logging.debug("Sending notification to Apprise. target=%s, addresses=%s" % (item.target, addresses))
        to = ','.join(addresses)

        # Disable the Apprise rate limiting subsystem.
        try:
            from apprise.plugins.NotifyBase import NotifyBase
            NotifyBase.request_rate_per_sec = 0
        except ImportError:
            pass

        # Create an Apprise instance.
        apobj = apprise.Apprise(asset=apprise.AppriseAsset(async_mode=False))

        # Collect URL parameters.
        params = OrderedDict()

        # Obtain and apply all possible Apprise parameters from data dictionary.
        params.update(obtain_apprise_arguments(item, APPRISE_ALL_ARGUMENT_NAMES))

        # Apply addressee information.
        if sender:
            params["from"] = sender
        if to:
            params["to"] = to
        if sender_name:
            params["name"] = sender_name

        # Add parameters to Apprise notification URL.
        uri = add_url_params(baseuri, params)
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
        srv.logging.error("Sending message using Apprise failed. target=%s, error=%s" % (item.target, e))
        return False
