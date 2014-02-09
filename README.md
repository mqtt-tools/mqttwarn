# mqtt2pushover

This program subscribes to any number of MQTT topics (including wildcards) and publishes received payloads to [pushover.net](https://pushover.net).

You associate topic branches to application keys (pushover terminology) in the configuration file (copy `sample-config.py` to `config.py` for use). For example:

```python
# Map MQTT topics (wildcards allowed!) to Pushover.net app keys
topicmap = {
    'home/events/owntracks/jpm/+' : 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', # owntracks
    'home/monitoring/#'           : 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', # icinga
    'oh/#'                        : 'mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm', # openhab
}
```

A message published to, say, `home/t1` will use the `zzzz` app key for the pushover message, while a message published to `oh/warning` will use the `mmmm` app key. This allows this program to notify your Android or iOS devices on different services.

## Obligatory screenshot

![pushover on iOS](screenshot.png)

## Requirements

* An MQTT broker (e.g. [Mosquitto](http://mosquitto.org))
* A [pushover.net](https://pushover.net/) account
* The Paho Python module: `pip install paho-mqtt`
* `pushover.py` (included) from [https://github.com/pix0r/pushover](https://github.com/pix0r/pushover)
