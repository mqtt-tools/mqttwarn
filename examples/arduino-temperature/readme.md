# Arduino » Enrich temperature readings


## About

Assuming we get, from an Arduino, say, a single numerical value in the payload
of an MQTT message, we want to generate JSON with some additional fields. Using
a [Jinja2] template for the task, does exactly what we need.


## Implementation

The following target configuration invokes the template:

```ini
[arduino/temp]
targets = log:info, http:graylog2
template = temp2json.json
```

The Jinja2 template looks like this.
```jinja
{#
    We expect a single numeric temperature value in `payload'.
    Return JSON suitable for Graylog2 (requires `host` and `short_message`).

    Define a data structure in Jinja2 and return it as a JSON string.
    Note how transformation data (produced within mqttwarn) is used:
    The variables `_dtiso` and `payload` carry the timestamp and the
    payload respectively.
#}
{% set data = {
	'host':          topic,
	'short_message': "Heat " + payload,
	'tst':           _dtiso,
	'temperature':   payload,
	'woohooo':       17,
	}
	%}
{{ data | jsonify }}
```

An example JSON string returned by that template is then passed to the
configured targets.
```json
{"host": "arduino/temp", "woohooo": 17, "tst": "2014-04-13T09:25:46.247150Z", "temperature": "22", "short_message": "Heat 22"}
```


[Jinja2]: https://jinja.palletsprojects.com/templates/
