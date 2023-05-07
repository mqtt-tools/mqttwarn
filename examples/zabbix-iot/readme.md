# Forwarding data from IoT devices to Zabbix


## About
 
This tutorial describes how to receive measurement or metric values in JSON format,
for example from IoT devices running [Tasmota] or [ESPEasy], and converge them into
[Zabbix], using mqttwarn's [Zabbix service plugin].

:::{note}
This tutorial has been conceived in the time of the advent of the venerable ESP8266 processors,
where networking with embedded devices was made affordable, and projects like
[Battery Powered ESP8266 IoT – Temperature Sensor] or [Battery Powered ESP8266 WiFi Temperature
and Humidity Logger] have been conceived and demonstrated their applications.
:::


## Configuration

As an example, let's consider we wish to capture temperature and humidity data from an
MQTT topic like `tele/<device>/<metric>`, for example `tele/bathroom/temperature` and
`tele/bathroom/humidity`.

In order to implement it, use the following mqttwarn configuration file, and the
accompanying user-defined functions file.

:::{literalinclude} mqttwarn-zabbix-iot.ini
:language: ini
:::

:::{literalinclude} mqttwarn-zabbix-iot.py
:language: python
:::

To complete the setup, we need to create a host (or more hosts) in Zabbix with the corresponding device
name that delivers the value ((part[1]) in `udf.py`). At last, we need to create a [Zabbix trapper] item
on this host.
```
Name: <trapper name>    # Anything you like, I named it `mqtt_temp`. 
Type: zabbix_trapper
Key:  <metric name>     # Must correspond with the third part (part[2]) of the decoded MQTT topic, for example `temperature`.
Type: numeric (float)
```


## Usage

Using three terminal sessions, you can exercise the example interactively. First, let's start
the [Mosquitto] MQTT broker.
```shell
docker run --name=mosquitto -it --rm --publish=1883:1883 eclipse-mosquitto:2.0 mosquitto -c /mosquitto-no-auth.conf
```

Let's acquire the configuration assets, and start `mqttwarn`.
```shell
wget https://github.com/mqtt-tools/mqttwarn/raw/main/examples/zabbix-iot/mqttwarn-zabbix-iot.ini
wget https://github.com/mqtt-tools/mqttwarn/raw/main/examples/zabbix-iot/mqttwarn-zabbix-iot.py
mqttwarn --config-file=mqttwarn-zabbix-iot.ini
```

Now, when publishing a metric value to the designated MQTT topic, `mqttwarn` will provision a Zabbix
host and trapper, and submit the metric to it. 
```shell
echo '42.42' | mosquitto_pub -t 'tele/bathroom/temperature' -l
```

After publishing a value to the topic, for example `tele/bathroom/temperature`, you should be able to
see this value in Zabbix at the host named `bathroom`, with the item name `temperature`.


[Battery Powered ESP8266 IoT – Temperature Sensor]: https://homecircuits.eu/blog/battery-powered-esp8266-iot-logger/
[Battery Powered ESP8266 WiFi Temperature and Humidity Logger]: https://github.com/tzapu/DeepSleepDHT22
[ESP8266]: https://en.wikipedia.org/wiki/ESP8266
[ESPEasy]: https://github.com/letscontrolit/ESPEasy
[Mosquitto]: https://mosquitto.org
[Tasmota]: https://github.com/arendst/Tasmota
[Zabbix]: https://www.zabbix.com/
[Zabbix service plugin]: https://mqttwarn.readthedocs.io/en/latest/notifier-catalog.html#zabbix
[Zabbix trapper]: https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/trapper
