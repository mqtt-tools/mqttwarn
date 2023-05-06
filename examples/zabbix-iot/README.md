# Forwarding measurement/metric values from IoT devices to Zabbix


## About
 
This tutorial describes how to receive measurement or metric values in JSON format,
for example from IoT devices running [Tasmota] or [ESPEasy], and converge them into
[Zabbix], using mqttwarn's [Zabbix service plugin].


## Configuration

As an example, let's consider we wish to capture temperature and humidity data from an
MQTT topic like `tele/<device>/<metric>`, for example `tele/bathroom/temperature` and
`tele/bathroom/humidity`.

To achieve this, we add following settings to `/opt/mqttwarn/mqttwarn.ini`.
```ini
functions = 'udf.py'

[config:zabbix]
targets = {
    't1'  : [ 'localhost', 10051 ],
  }

[tele/#]
alldata = decode_for_zabbix()
targets = zabbix:t1
```

In the file `/opt/mqttwarn/udf.py`, we add the `decode_for_zabbix` decoder function.
```python
def decode_for_zabbix(topic, data, srv=None):
    status_key = None

    # the first part (part[0]) is always tele
    # the second part (part[1]) is the device, the value comes from
    # the third part (part[2]) is the name of the metric (e.g. temperature/humidity/voltage...)
    parts = topic.split('/')
    client = parts[1]
    key = parts[2]

    return dict(client=client, key=key, status_key=status_key)
```

To complete the setup, we need to create a host (or more hosts) in Zabbix with the corresponding device
name that delivers the value ((part[1]) in `udf.py`). At last, we need to create a [Zabbix trapper] item
on this host.
```
Name: <trapper name>    # Anything you like, I named it `mqtt_temp`. 
Type: zabbix_trapper
Key:  <metric name>     # Must correspond with the third part (part[2]) of the decoded MQTT topic, for example `temperature`.
Type: numeric (float)
```

After publishing a value to the topic, for example `tele/bathroom/temperature`, you should be able to
see this value in Zabbix at the host named `bathroom`, with the item name `temperature`.

:::{note}
This tutorial has been conceived in the time of the advent of the venerable ESP8266 processors,
where networking with embedded devices was made affordable, and projects like
[Battery Powered ESP8266 IoT – Temperature Sensor] or [Battery Powered ESP8266 WiFi Temperature
and Humidity Logger] have been conceived and demonstrated their applications.
:::


[Battery Powered ESP8266 IoT – Temperature Sensor]: https://homecircuits.eu/blog/battery-powered-esp8266-iot-logger/
[Battery Powered ESP8266 WiFi Temperature and Humidity Logger]: https://github.com/tzapu/DeepSleepDHT22
[ESP8266]: https://en.wikipedia.org/wiki/ESP8266
[ESPEasy]: https://github.com/letscontrolit/ESPEasy
[Tasmota]: https://github.com/arendst/Tasmota
[Zabbix]: https://www.zabbix.com/
[Zabbix service plugin]: https://mqttwarn.readthedocs.io/en/latest/notifier-catalog.html#zabbix
[Zabbix trapper]: https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/trapper
