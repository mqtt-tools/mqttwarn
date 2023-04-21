__author__ = "Andreas Motl <andreas.motl@panodata.org>"
__copyright__ = "Copyright 2023 Andreas Motl"
__license__ = "Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"

import dataclasses
import logging
from collections import OrderedDict
import typing as t
from pathlib import Path

import requests
from funcy import project

from mqttwarn.model import Service, ProcessorItem

DataDict = t.Dict[str, t.Union[str, bytes]]


# Field names to be propagated from transformation data to ntfy API.
#
# `topic` will be omitted, and not picked from the transformation
# data, because it contains the MQTT topic already, and would cause
# collisions. The topic is exclusively defined using the `url` field,
# see https://mqttwarn.readthedocs.io/en/latest/notifier-catalog.html#ntfy.
#
# All other ntfy fields are enumerated here.
# https://docs.ntfy.sh/publish/#publish-as-json

NTFY_FIELD_NAMES: t.List[str] = [
    # "topic",
    "message",
    "title",
    "tags",
    "priority",
    "actions",
    "click",
    "attach",
    "filename",
    "delay",
    "email",
]

logger = logging.getLogger(__name__)


# The `requests` session instance, for running HTTP requests.
http = requests.Session()
# TODO: Add mqttwarn version.
http.headers.update({"User-Agent": "mqttwarn"})


@dataclasses.dataclass
class NtfyRequest:
    """
    Manage parameters to be propagated to the ntfy HTTP API.
    """

    url: str
    options: t.Dict[str, str]
    fields: DataDict
    attachment_path: t.Optional[str]
    attachment_data: t.Optional[t.Union[bytes, t.IO]]

    def to_http_headers(self) -> t.Dict[str, str]:
        """
        Provide a variant for `fields` to be submitted as HTTP headers to the ntfy API.

        Python's `http.client` will, according to the HTTP specification,
        encode header values using the `latin-1` character set.

        In this spirit, the header transport does not permit any fancy UTF-8 characters
        within any field, so they will be replaced with placeholder characters `?`.
        """
        return dict_ascii_clean(dict_with_titles(self.fields))


def plugin(srv: Service, item: ProcessorItem) -> bool:
    """
    mqttwarn service plugin for ntfy.
    """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # Decode inbound mqttwarn job item into `NtfyRequest`.
    ntfy_request = decode_jobitem(item)

    # Convert field dictionary to HTTP header dictionary.
    headers = ntfy_request.to_http_headers()
    srv.logging.debug(f"Headers: {dict(headers)}")

    # Submit request to ntfy HTTP API.
    try:
        srv.logging.info("Sending notification to ntfy. target=%s, options=%s", item.target, ntfy_request.options)
        response = http.put(ntfy_request.url, data=ntfy_request.attachment_data, headers=headers)
        response.raise_for_status()
    except Exception:
        srv.logging.exception("Request to ntfy API failed")
        return False

    # Report about ntfy response.
    srv.logging.debug(f"ntfy response status: {response}")
    srv.logging.debug(f"ntfy response content: {response.content!r}")

    srv.logging.info("Successfully sent message using ntfy")

    return True


def decode_jobitem(item: ProcessorItem) -> NtfyRequest:
    """
    Decode inbound mqttwarn job item into `NtfyRequest`.
    """

    title = item.title
    body = item.message
    options: t.Dict[str, str]

    if isinstance(item.addrs, str):
        options = {"url": item.addrs}
    elif isinstance(item.addrs, dict):
        options = item.addrs
    else:
        raise TypeError(f"Unable to handle `targets` address descriptor data type `{type(item.addrs).__name__}`: {item.addrs}")

    url = options["url"]
    attachment_path = options.get("file")

    # Collect ntfy fields.
    fields: DataDict = OrderedDict()

    # Obtain and propagate all possible ntfy fields from transformation data.
    fields.update(obtain_ntfy_fields(item))

    # Overwrite title and message explicitly, when not present already.
    title and fields.setdefault("title", title)
    body and fields.setdefault("message", body)

    # Attach a file, or not.
    attachment_data = None
    if attachment_path:
        attachment_path, attachment_data = load_attachment(attachment_path, item.data)
        if attachment_data:
            # TODO: Optionally derive attachment file name from title, using `slugify(title)`.
            fields.setdefault("filename", Path(attachment_path).name)

    ntfy_request = NtfyRequest(
        url=url,
        options=options,
        fields=fields,
        attachment_path=attachment_path,
        attachment_data=attachment_data,
    )

    return ntfy_request


def obtain_ntfy_fields(item: ProcessorItem) -> DataDict:
    """
    Obtain eventual ntfy fields from transformation data.
    """
    fields_data = item.data and project(item.data, NTFY_FIELD_NAMES) or {}
    fields_addrs = item.addrs and project(item.addrs, NTFY_FIELD_NAMES) or {}
    fields_config = item.config and project(item.config, NTFY_FIELD_NAMES) or {}
    fields: DataDict = OrderedDict()
    fields.update(fields_config)
    fields.update(fields_addrs)
    fields.update(fields_data)
    return fields


def load_attachment(path: str, tplvars: t.Optional[DataDict]) -> t.Tuple[str, t.Optional[t.IO]]:
    """
    Load attachment file from filesystem gracefully.
    """
    data = None
    try:
        path = path.format(**tplvars or {})
    except:
        logger.exception(f"ntfy: Computing attachment file name failed")
    if path:
        try:
            data = open(path, "rb")
        except:
            logger.exception(f"ntfy: Accessing attachment file failed: {path}")
    return path, data


def ascii_clean(data: t.Union[str, bytes]) -> str:
    """
    Return ASCII-clean variant of input string.
    https://stackoverflow.com/a/18430817
    """
    if isinstance(data, bytes):
        data = data.decode()
    if isinstance(data, str):
        return data.encode("ascii", errors="replace").decode()
    else:
        raise TypeError(f"Unknown data type to compute ASCII-clean variant: {type(data).__name__}")


def dict_ascii_clean(data: DataDict) -> t.Dict[str, str]:
    """
    Return dictionary with ASCII-clean keys and values.
    """

    outdata = OrderedDict()
    for key, value in data.items():
        key = ascii_clean(key).strip()
        value = ascii_clean(value).strip()
        outdata[key] = value
    return outdata


def dict_with_titles(data: DataDict) -> DataDict:
    """
    Return dictionary with each key title-cased, i.e. uppercasing the first letter.

    >>> {"foo": "bar"}
    {"Foo": "bar"}
    """
    outdata = OrderedDict()
    for key, value in data.items():
        outdata[key.title()] = value
    return outdata
