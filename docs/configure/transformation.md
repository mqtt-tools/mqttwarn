(configure-transformation)=
(transformations)=
# Transformations


## Introduction

This section of the documentation will outline how to configure basic and
advanced data transformations to apply to the data processed by mqttwarn.

You will learn how to leverage corresponding options on configuration sections
for mqttwarn [topics](#topics), like `format`, `template`, `filter`, and 
`alldata`, in order to manipulate the outbound data destined to the
[services](#services).


## Overview

This guideline starts out easy, but will advance to more sophisticated 
configuration details and examples. Please read this document carefully.

+ [Verbatim forwarding](#verbatim-forwarding)
+ [Basic formatting](#basic-formatting)
+ [Template files](#template-files)
+ [Decoding JSON](#decoding-json)
+ [Decoding nested JSON](#decoding-nested-json)
+ [User-defined functions](#user-defined-functions)
+ [User-defined function examples](#user-defined-function-examples)


## Verbatim forwarding

To simply forward an incoming MQTT message without any transformations, you don't
need to do anything other than configure the target. Add a topic section to your 
`mqttwarn.ini`, by simply naming it after the topic you wish to have forwarded, 
and within the configuration section body, define the `targets` option. 

The payload of the inbound message will then be forwarded to the defined 
[](#service) plugin. Whether it simply says "ON", or contains a large JSON 
dictionary, is of no concern, because the message is forwarded verbatim.

```ini
[office/ups]
targets = log:debug
```

This example demonstrates how to subscribe to messages on the MQTT topic
`office/ups`, and save them into the `mqttwarn.log` file with a `debug` label.

:::{note}
This assumes that you have configured the log section the way described at the 
[](#configure-service).
:::


(transformation-data)=
## Transformation data

The information that is available to you in creating the outbound message is called
"the transformation data". A very basic set of transformation data is the following:
```python
{
  "topic":      "foo/bar",                      # MQTT topic
  "payload":    "Hello world!",                 # MQTT message payload
  "_dtepoch":   1392628581,                     # "epoch time"
  "_dtiso":     "2014-02-17T10:38:43.910691Z",  # ISO date (UTC)
  "_dthhmm":    "10:16",                        # timestamp HH:MM (local)
  "_dthhmmss":  "10:16:21",                     # timestamp HH:MM:SS (local)
}
```
The transformation data can be extended by running [decoding](#decoding) functions. 


(format)=
## Basic formatting

mqttwarn provides several options to create a different outbound message,
allowing you, for example, to make it more human-readable.

The most basic option is called "formatting". The `title` and `format` options 
define the **title** and the **body** of the outbound message. With that feature,
you can turn an MQTT payload that simply states "ON", into a friendlier version. 

Both options effectively define template strings, where transformation data 
variables can be interpolated into.

```ini
[office/ups]
title  = Office UPS
format = The office UPS is {payload}
```

Please note that the original MQTT payload is referenced per `payload` variable, 
so that if the UPS is switched off, and sends out a corresponding MQTT message, 
the outbound message will state it so.


## Template files

Instead of formatting output with the `format` specification as described 
above, _mqttwarn_ can render the output message with [Jinja2 templates]. 
This is particularly interesting for the `smtp`, `nntp`, and `file` targets.

Consider the following example [topic](#topics) configuration, where we 
illustrate using the `template` option instead of `format`.

```ini
[nn/+]
targets = nntp:jpaa
; format = {name}: {number} => {_dthhmm}
template = demo.j2
```

_mqttwarn_ loads [Jinja2 templates] from the `templates/` directory relative
to the configured `directory`.

### Example
Assuming we have the following template file `templates/demo.j2`:

```jinja
{#
    this is a comment
    in Jinja2
    See https://jinja.palletsprojects.com/templates/ for information
    on Jinja2 templates.
#}
{% set upname = name | upper %}
{% set width = 60 %}
{% for n in range(0, width) %}-{% endfor %}

Name.................: {{ upname }}
Number...............: {{ number }}
Timestamp............: {{ _dthhmm }}
Original payload.....: {{ payload }}
```

After processing, it will produce the following outcome, which will be
forwarded to any target which uses this configuration.

```text
------------------------------------------------------------
Name.................: JANE JOLIE
Number...............: 47
Timestamp............: 19:15
Original payload.....: {"name":"Jane Jolie","number":47, "id":91}
```

### More details

The template variable `{{ payload }}` will interpolate the original MQTT message 
payload into the template string.

If the payload was JSON, its content is also decoded and available as template
variables, together with all the other transformation data.

If the template cannot be rendered, say, if it contains a Jinja2 error, or if
the template file cannot be found, etc., the original raw message is used in
lieu on output.


## Decoding JSON

Other than just passing the payload received via MQTT to a service, _mqttwarn_ 
allows you to do the following:

* Transform payloads on a per-topic basis. For example, you know you will be 
  receiving JSON, but you want to warn with a nicely formatted message.
* For certain services, you can change the _title_ (or _subject_) of the outgoing message.
* For certain services, you can change the _priority_ of the outgoing message.

:::{note}
mqttwarn will gracefully attempt to decode inbound MQTT messages from JSON. If
it works, it will merge the content into the [](#transformation-data). If not,
nothing else happens, and the raw data will be available within the `payload`
field.
:::

:::{note}
Embedded `"\n"` are converted to newlines on output.
:::

### Example
Consider the following JSON payload published to the MQTT broker:

```shell
mosquitto_pub -t 'osx/json' -m '{"fruit":"banana", "price": 63, "tst" : "1391779336"}'
```

Using the `format` option, you can configure _mqttwarn_ to transform that JSON 
into a different outbound message, which is actually the text that will get 
submitted as notification. The `format` option is effectively a template string,
where transformation data variables can be interpolated into. 

```ini
format = "I'll have a {fruit} if it costs {price}"
```

The result is:

![OSX notifier](../assets/desktopnotify.jpg)


## Decoding nested JSON

Within templates and formats, you can only refer to the top-level names of an 
incoming JSON message, which significantly limits the kinds of messages 
`mqttwarn` can process. Currently, you will need to flatten your document
using an `alldata` transformation function.

That means, you should build a new JSON message with _only_ top-level values, 
where you pick values of interest from your nested JSON document.

:::{todo}
We are looking into providing a generic way to access nested elements at 
[access nested elements in JSON payloads](https://github.com/mqtt-tools/mqttwarn/issues/303).
In the meanwhile, for doing it in a custom way, please have a look at the
(#nested-json-example).
:::


## Transforming JSON

When receiving JSON data like `{"data": {"humidity": 62.18}}`, you might
want to extract values using the `format` mechanism before forwarding
it to other data sinks.
```ini
format = "{data}"
```

However, by default, the outcome will be the string-serialized form of the
Python representation, `{'humidity': 62.18}`, which could not be what you
want if your data sink is expecting JSON format again.

To make it work as intended, you should use appropriate type coercion
for JSON data using the `!j` suffix.
```ini
format = "{data!j}"
```

This will serialize the formatted data to JSON format appropriately,
so the outbound message will be `{"humidity": 62.18}`.


## User-defined functions

You can define custom code to be invoked on different stages of the processing
pipeline. This is a powerful utility.
If you are in a hurry, you can skip the documentation, and get inspired what
you can do by [exploring user-defined functions by example](#user-defined-function-examples).


### Introduction

A [topic section](#topics) in the configuration file can have different 
[topic options](#topic-options) defined, some of them are callbacks where you
can configure user-defined [Python functions](inv:python#tut-functions). It
works for all of those options:

- `filter` : boolean, or a function that returns a boolean
- `alldata` : dictionary, or a function that returns a dictionary
- `title` : string, or a function that returns a string
- `format` : string, or a function that returns a string
- `image` : see below
- `priority` : see below

Those [topic options](#topic-options) *do **not** accept* a user-defined function:

- `targets`
- `topic`
- `qos`


### Getting started

You will start out by telling mqttwarn where to find your Python code.
Edit the `mqttwarn.ini` configuration file, navigate to the `[defaults]`
section, and configure the `functions` option appropriately.
```ini
[defaults]
; Path to file containing user-defined functions like `format` or `alldata`.
functions = 'udf.py'
```

Then, in the [topic section](#topics), define the MQTT topic to subscribe to,
and configure the user-defined function for the `format` option. That's it.
```ini
[test/topic]
format = my_function()
```

:::{note}
When relative file names are configured at the `functions` option, they will
be resolved from the directory of the `mqttwarn.ini` file, which is, by default,
the `/etc/mqttwarn` directory.

In order to create a blueprint file for your `udf.py`, you can use the
`mqttwarn make-udf` command.
:::


### Filtering

Within the mqttwarn processing pipeline, filtering functions will be invoked
first, and will permit you to terminate processing early.

A function called from the `filter` option in a [topic section](#topics) needs
to return `True` to stop the outbound notification. It obtains `topic`,
`payload`, `section`, and `srv` arguments, where `payload` is the MQTT message
payload as a [Python string](inv:python#tut-strings) decoded from UTF-8.

The function signature looks like this.
```python
from mqttwarn.model import Service

def example_filter(topic: str, payload: str, section: str, srv: Service):
    pass
```

(decode)=
(decoding)=
### Decoding

After filtering, mqttwarn will invoke the decoding step, using the function
defined by the `alldata` option in a [topic section](#topics).

The function is expected to either return a Python [dictionary](inv:python#tut-dictionaries),
or `None`. It obtains `topic`, `data`, and `srv` arguments, where `data` is 
also a [dictionary](inv:python#tut-dictionaries) wrapping the inbound MQTT 
message, see [transformation data](#transformation-data). The returned data 
is merged into the transformation data. 

The function signature looks like this.
```python
from mqttwarn.model import Service
from typing import Any, Dict

def example_alldata(topic: str, data: Dict[str, Any], srv: Service):
    pass
```

The keys in the dictionary returned from this function can be used when
describing the outbound message by using the `title` and `format` options
of the same [topic section](#topics), see also [](#format).


### Formatting

Both the `title` and the `format` options in the topic section can contain a
string where `{bracketed}` references get resolved using the transformation data
returned from the data mapping function `alldata`, see also [](#format).

Alternatively, they can call a function that returns a string that may or may not 
contain such references. The functions called here do not have access to the actual 
dictionary returned from data mapping functions, though.

For example, a minimal user-defined function suitable for the `format` option,
effectively doing nothing, looks like this.
```python
def noop_formatter(data, srv=None):
    return data
```

```ini
[test/topic]
format = noop_formatter()
```

:::{attention}
If a function operating on a message, for example within `format =`, returns
`None`, or an empty string, the target notification is suppressed.
:::

:::{todo}
Should the detail "do not have access to the actual dictionary" be improved
in one way or another? 
:::


### The `Service` object

What is common to all user-defined functions is that they will receive inbound
data from mqttwarn, and it is your obligation to return outbound data or
signal information back.

Optionally, the user-defined functions will obtain a `srv` argument, which 
is an object with a few helper functions, and, at the same time, provides
access to internal machinery like the instance of the `paho.mqtt.client.Client` 
object (which provides a plethora of properties and methods), to the `mqttwarn` 
logger instance, to the Python `globals()` method and all that entails, and to 
the name of the program currently being executed.

This example function will give you an idea how to use those features. 
```python
from mqttwarn.model import Service
from typing import Dict

def publishing_formatter(data: Dict[str, str], srv: Service):
    message = "¡Hola!"
    srv.logging.info(f"+++++++++++ {message}")
    srv.mqttc.publish("topic/response", message, qos=0, retain=False)
    return message
```

:::{attention}
Be advised that if you publish back to the same MQTT topic which triggered
the invocation of your function, you will create an endless loop.
:::


## User-defined function examples

In this section, you can explore a few example scenarios where user-defined
functions are being used.


### `format`: Replacing incoming payloads

The `format` option will be evaluated at the last stage of the processing
pipeline. The string returned by a corresponding function replaces the outgoing
`message` slot completely.

Consider the following user-defined function,
```python
from mqttwarn.model import Service
from typing import Any

def example_formatter(data: Any, srv: Service):
    """
    An example formatting function.
    
    >>> example_formatter({"fruit": "pineapple"})
    'Ananas'
    """
    if isinstance(data, dict) and "fruit" in data:
        return "Ananas"
    return None
```

and this configuration snippet which uses that function, instead of a string
template,
```ini
[defaults]
; Path to file containing self-defined functions like `format` or `alldata`.
functions = 'udf.py'

[test/topic]
#format = Since when does a {fruit} cost {price}?
format = example_formatter()
```

and see how it works:
```
in/a1 {"fruit":"pineapple", "price": 131, "tst" : "1391779336"}
out/food Ananas
out/fruit/pineapple Ananas
```

:::{note}
When the inbound data can be decoded from JSON, the `format` function will be
invoked with decoded JSON as well. The `data` argument will then obtain a
Python [dictionary](inv:python#tut-dictionaries). Otherwise, the function will
obtain the raw inbound message payload.
:::

:::{tip}
In the same spirit, you are usually not returning JSON here. _If_ you want to
return JSON, make sure to serialize it to a string on your own behalf.
:::


### `filter`: Filtering notifications

A notification can be filtered (or suppressed, or ignored) by a user-defined
function, by configuring the `filter` option within a [topic section](#topics).
```ini
[owntracks/#/phone]
filter = owntracks_filter()
```

Now, when a message for the defined topic `owntracks/jane/phone` is received, 
the function `owntracks_filter()` will be invoked to determine whether to 
process the message.

The filter function should return `True` if the message should be suppressed, 
or `False` if the message should be processed. This is a basic but working
example for such a filter function.
```python
from mqttwarn.model import Service

def owntracks_filter(topic: str, message: str, section: str, srv: Service):
    """
    Only process messages containing "event", skip all others.
    
    >>> owntracks_filter("owntracks/jane/phone", "event: something significant")
    False

    >>> owntracks_filter("owntracks/jane/phone", "trace: something else")
    True
    """
    is_event_message = message.find("event") != -1
    return not is_event_message
```

:::{note}
The `topic` parameter will be the name of the specific topic that the message
was received on, here `owntracks/jane/phone`. The name of the section will be 
the `section` argument, here `owntracks/#/phone`.
:::

(decode-topic)=
### `alldata`: Decoding topic names

Use case: An MQTT topic contains information you want to use in transformations.

As an example, let's consider the [OwnTracks] system. When an [OwnTracks] device
detects a change of a configured [waypoint] or [geo-fence], it emits a JSON payload 
which looks like this, on a topic like `owntracks/<username>/<deviceid>`. For example:
```
owntracks/jane/phone {"_type": "location", "lat": "52.4770352", "desc": "Home", "event": "leave"}
```

In order to obtain the username (`jane`) and her device name (`phone`) from the
MQTT topic, and use it within the outbound message, we need to [decode](#decode)
it into the transformation data. To accomplish that, add a user-defined function, 
and assign it to the `alldata` option within the configuration file.

This specifies that when a message for the defined topic `owntracks/jane/phone` 
is processed, the user-defined function `decode_owntracks_topic()` should be
invoked to transform the data. Topic names may also contain MQTT wildcards.
```ini
[owntracks/jane/phone]
alldata = decode_owntracks_topic()
```

The function we define to do that, looks like this:
```python
def decode_owntracks_topic(topic):
    """
    Decode an OwnTracks MQTT topic like `owntracks/<username>/<device>`.
    
    >>> decode_owntracks_topic("owntracks/jane/phone")
    {'username': 'jane', 'device': 'phone'}
    """
    if isinstance(topic, str):
        try:
            parts = topic.split('/')
            username = parts[1]
            device_id = parts[2]
        except:
            username = 'unknown'
            device_id = 'unknown'
        return dict(username=username, device=device_id)
    return None
```

The returned [dictionary](inv:python#tut-dictionaries) is merged into the
transformation data, i.e. it is made available to plugins and to 
[formatters](#format).

Now, if we then create a `format` rule like
```ini
format = {username}@{device}: {event} => {desc}
```

the user-defined function will transform it into an outbound message as directed.
```text
jane@phone: leave => Home
```


(decode-nested-json)=
### `alldata`: Decoding nested JSON

Use case: Say we are receiving messages from a temperature sensor running
[Tasmota], and we wish to convert them into [InfluxDB line format].

The incoming [Tasmota JSON status response for a DS18B20 sensor] looks like this. 
```json
{
    "Time": "2018.02.01 21:29:40",
    "DS18B20": {
      "Temperature": 19.7
    },
    "TempUnit": "C"
},
```

Since the nested `Temperature` item cannot be referenced directly within a
`format` definition, we need to make it a top-level value of the transformation
data. While we are at it, we can change the date to milliseconds since the epoch,
and also include the MQTT topic.
```json
{
    "topic": "tasmota/temp/ds/1", 
    "timestamp": 1517525319000, 
    "temperature": 19.7
}
```

This can be accomplished with the following user-defined function. 
```python
import ast
import logging
import time

from datetime import datetime
from typing import Dict
from mqttwarn.model import Service

def ds18b20_values(topic: str, data: Dict[str, str], srv: Service):
    payload = ast.literal_eval(data["payload"])
    ts = datetime.strptime(payload["Time"], "%Y.%m.%d %H:%M:%S")
    millis = int(time.mktime(ts.timetuple()) * 1000)
    temp = payload["DS18B20"]["temperature"]
    outdata = dict( topic = topic, temperature = temp, timestamp = millis )
    logging.debug(outdata)
    return outdata
```

When applying it to a topic,
```ini
[tasmota/temp/ds/+]
targets = log:info
alldata = ds18b20_values()
format  = weather,topic={topic} temperature={temperature} {timestamp}
```

mqttwarn will format the outbound message like this.
```text
weather,topic=tasmota/temp/ds/1 temperature=19.7 1517525319000
```


[geo-fence]: https://en.wikipedia.org/wiki/Geo-fence
[InfluxDB line format]: https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_tutorial/
[Jinja2 templates]: https://jinja.palletsprojects.com/templates/
[Tasmota]: https://github.com/arendst/Tasmota
[Tasmota JSON status response for a DS18B20 sensor]: https://tasmota.github.io/docs/JSON-Status-Responses/#ds18b20
[OwnTracks]: https://owntracks.org
[waypoint]: https://en.wikipedia.org/wiki/Waypoint
