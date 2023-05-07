# -*- coding: utf-8 -*-
# (c) 2014-2023 The mqttwarn developers

__author__ = "Jan-Piet Mens <jpmens()gmail.com>, Ben Jones <ben.jones12()gmail.com>"
__copyright__ = "Copyright 2014-2022 Jan-Piet Mens"
__license__ = "Eclipse Public License - v 2.0 (http://www.eclipse.org/legal/epl-2.0/)"

try:
    from importlib.metadata import version
except ImportError:  # pragma: nocover
    from importlib_metadata import version  # type: ignore[no-redef]

__version__ = version("mqttwarn")
