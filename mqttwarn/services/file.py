#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import io
import tempfile


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    mode = "a"

    # item.config is brought in from the configuration file
    config = item.config

    # Evaluate global parameters.
    newline = False
    overwrite = False
    if type(config) == dict and 'append_newline' in config and config['append_newline']:
        newline = True
    if type(config) == dict and 'overwrite' in config and config['overwrite']:
        overwrite = True

    # `item.addrs` is either a dict or a list associated with a particular target.
    # While lists may contain more than one item (e.g., for the pushover target),
    # the `file` service only allows for single items, the path name.
    # When it's a dict, additional parameters can be obtained to augment the
    # behavior of the write operation on a per-file basis.
    if isinstance(item.addrs, dict):
        filename = item.addrs['path'].format(**item.data)
        # Evaluate per-file parameters.
        newline = item.addrs.get('append_newline', newline)
        overwrite = item.addrs.get('overwrite', overwrite)
    else:
        filename = item.addrs[0].format(**item.data)

    # Interpolate some variables into filename.
    if "$TMPDIR" in filename:
        filename = filename.replace("$TMPDIR", tempfile.gettempdir())

    srv.logging.info("Writing to file `%s'" % (filename))

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    if newline:
        text += "\n"
    if overwrite:
        mode = "w"

    if isinstance(text, bytes):
        mode += "b"
        encoding = None
    else:
        encoding = "utf-8"

    try:
        f = io.open(filename, mode=mode, encoding=encoding)
        f.write(text)
        f.close()

    except Exception as e:
        srv.logging.error("Cannot write to file `%s': %s" % (filename, e))
        return False

    return True
