__author__ = "Andreas Motl <andreas.motl@panodata.org>"
__copyright__ = "Copyright 2023 Andreas Motl"
__license__ = "Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"

import dataclasses
import logging
import re
from collections import OrderedDict
import typing as t
from email.header import Header
from pathlib import Path

import requests
from funcy import project, merge

from mqttwarn.model import Service, ProcessorItem
from mqttwarn.util import Formatter, asbool, load_file

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
# https://docs.ntfy.sh/publish/#list-of-all-parameters

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
    "icon",
    "email",
    "cache",
    "firebase",
    "unifiedpush",
]

NTFY_RFC2047_FIELDS: t.List[str] = [
    "message",
    "title",
    "tags",
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

    def to_http_headers(self, no_message: t.Optional[bool] = False) -> t.Dict[str, str]:
        """
        Provide a variant for `fields` to be submitted as HTTP headers to the ntfy API.

        Python's `http.client` will, according to the HTTP specification,
        encode header values using the `latin-1` character set.

        In this spirit, the header transport does not permit any fancy UTF-8 characters
        within any field, so they will be replaced with placeholder characters `?`.
        """
        data = dict_with_titles(encode_ntfy_fields(self.fields))
        if no_message and "Message" in data:
            del data["Message"]
        return data


def plugin(srv: Service, item: ProcessorItem) -> bool:
    """
    mqttwarn service plugin for ntfy.

    Regarding newline support, this procedure implements the following suggestion by @codebude from [1]:

    - Per default, send the message as HTTP body, enabling line breaks.
    - When submitting a local attachment without a text message, encode the
      attachment data into the HTTP body, and all other fields into HTTP headers.
    - When it is a notification with both a local attachment, and a text message,
      also encode the attachment data into the HTTP body, but replace all newline
      characters `\n` of the text message, because they can not be encoded into
      HTTP headers.

    [1] https://github.com/mqtt-tools/mqttwarn/issues/677#issuecomment-1575060446
    """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # Decode inbound mqttwarn job item into `NtfyRequest`.
    ntfy_request = decode_jobitem(item)

    # Submit request to ntfy HTTP API.
    srv.logging.info("Sending notification to ntfy. target=%s, options=%s", item.target, ntfy_request.options)
    try:
        if ntfy_request.attachment_data is not None:
            # HTTP PUT: Use body for attachment, convert field dictionary to HTTP header dictionary.
            headers = ntfy_request.to_http_headers()
            body = ntfy_request.attachment_data
            response = http.put(
                ntfy_request.url,
                data=body,
                headers=headers,
            )
            srv.logging.debug(f"Headers: {dict(headers)}")
        else:
            # HTTP POST: Use body for message, other fields via HTTP headers.
            headers = ntfy_request.to_http_headers(no_message=True)
            body = to_string(ntfy_request.fields["message"]).encode("utf-8")
            response = http.post(
                ntfy_request.url,
                data=body,
                headers=headers,
            )
    except Exception:
        srv.logging.exception("Request to ntfy API failed")
        return False
    srv.logging.debug(f"Body:    {body!r}")
    srv.logging.debug(f"Headers: {dict(headers)}")

    try:
        response.raise_for_status()
    except Exception:
        srv.logging.exception(f"Error response from ntfy API:\n{response.text}")
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
    settings: t.Dict[str, t.Union[str, int, float, bool]] = {}

    if isinstance(item.addrs, str):
        item.addrs = {"url": item.addrs}
    elif isinstance(item.addrs, dict):
        pass
    else:
        raise TypeError(f"Unable to handle `targets` address descriptor data type `{type(item.addrs).__name__}`: {item.addrs}")

    # Decode options from target address descriptor.
    options = item.addrs

    url = options["url"]
    attachment_path = options.get("file")

    # Extract settings, purging them from the target address descriptor afterwards.
    if "__settings__" in options:
        if isinstance(options["__settings__"], t.Dict):
            settings = dict(options["__settings__"])
            del options["__settings__"]

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
        try:
            attachment_path = attachment_path.format(**item.data or {})
            try:
                attachment_data = load_file(
                    path=attachment_path,
                    retry_tries=settings.get("file_retry_tries"),
                    retry_interval=settings.get("file_retry_interval"),
                    unlink=asbool(settings.get("file_unlink")),
                )
                if attachment_data:
                    # TODO: Optionally derive attachment file name from title, using `slugify(title)`.
                    fields.setdefault("filename", Path(attachment_path).name)
            except Exception as ex:
                logger.exception(f"ntfy: Attaching local file failed. Reason: {ex}")
        except:
            logger.exception("ntfy: Computing attachment file name failed")

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
    Obtain eventual ntfy fields from different sources.
    """

    # Get relevant ntfy option fields from all of `config`,
    # `addrs`, and `data`, with ascending precedence.
    fields_data = item.data and project(item.data, NTFY_FIELD_NAMES) or {}
    fields_addrs = item.addrs and project(item.addrs, NTFY_FIELD_NAMES) or {}
    fields_config = item.config and project(item.config, NTFY_FIELD_NAMES) or {}
    fields: DataDict = OrderedDict()
    fields.update(fields_config)
    fields.update(fields_addrs)
    fields.update(fields_data)

    # Run an interpolation step also on the outbound ntfy option
    # fields, in order to unlock using templated values there.
    logger.info((item.config or {}, item.addrs or {}, item.data or {}))
    all_data = merge(item.config or {}, item.addrs or {}, item.data or {})
    formatter = Formatter()
    for key, value in fields.items():
        if isinstance(value, str):
            new_value = formatter.format(value, **all_data)
            fields[key] = new_value

    return fields


def to_string(value: t.Union[str, bytes]) -> str:
    """
    Cast from string or bytes to string.
    """
    if isinstance(value, bytes):
        value = value.decode()
    return value


def ascii_clean(data: t.Union[str, bytes]) -> str:
    """
    Return ASCII-clean variant of input string.
    https://stackoverflow.com/a/18430817
    """
    data = to_string(data)
    if isinstance(data, str):
        return data.encode("ascii", errors="replace").decode()
    else:
        raise TypeError(f"Unknown data type to compute ASCII-clean variant: {type(data).__name__}")


def encode_rfc2047(data: t.Union[str, bytes]) -> str:
    """
    Return RFC2047-encoded variant of input string.

    https://docs.python.org/3/library/email.header.html
    """
    if isinstance(data, bytes):
        data = data.decode()
    if isinstance(data, str):
        return Header(s=data, charset="utf-8", maxlinelen=10000).encode()
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


def encode_ntfy_fields(data: DataDict) -> t.Dict[str, str]:
    """
    Return dictionary suitable for submitting to the ntfy HTTP API using HTTP headers.

    - The field values for `title`, `message` and `tags` are encoded using RFC 2047, aka.
      MIME Message Header Extensions for Non-ASCII Text.

    - The other field values will be stripped from any special characters to be ASCII-clean.

    Appendix

    When using RFC 2047, two encodings are possible. The Python implementation cited below
    seems to use the "Q" encoding scheme by default.

    4.1 The "B" encoding is identical to the "BASE64" encoding defined by RFC 2045.
    4.2 The "Q" encoding is similar to the "Quoted-Printable" content-transfer-encoding
        defined in RFC 2045.  It is designed to allow text containing mostly ASCII
        characters to be decipherable on an ASCII terminal without decoding.

    The Python email package supports the standards RFC 2045, RFC 2046, RFC 2047, and
    RFC 2231 in its `email.header` and `email.charset` modules.

    - https://datatracker.ietf.org/doc/html/rfc2047#section-2
    - https://datatracker.ietf.org/doc/html/rfc2047#section-4
    - https://docs.python.org/3/library/email.header.html
    """

    rm_newlines = re.compile(r"\r?\n")

    outdata = OrderedDict()
    for key, value in data.items():
        key = ascii_clean(key).strip()
        value = re.sub(rm_newlines, " ", to_string(value))
        if key in NTFY_RFC2047_FIELDS:
            value = encode_rfc2047(value)
        else:
            value = ascii_clean(value)
        outdata[key] = value
    return outdata


def dict_with_titles(data: t.Dict[str, str]) -> t.Dict[str, str]:
    """
    Return dictionary with each key title-cased, i.e. uppercasing the first letter.

    >>> {"foo": "bar"}
    {"Foo": "bar"}
    """
    outdata = OrderedDict()
    for key, value in data.items():
        outdata[key.title()] = value
    return outdata
