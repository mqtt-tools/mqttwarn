# mqtt2pushover

mqttwarn
mqttadvise
mqttell


This program subscribes to any number of MQTT topics (which may include wildcards) and publishes received payloads to one or more notification services, including support for notifying distinct services for the same message.

For example, you may wish to notify via e-mail and to Pushover of an alarm published as text to the MQTT topic `home/monitoring/+`.

Support for the following services is available:

* files (output to files on the file system)
* Pushover.net
* Twitter
* SMTP (e-mail)
* NMA
* Prowl
* XBMC
* Mac OS X notification center

Notifications are transmitted to the appropriate service via plugins which are easy to add.

You associate topic branches to application keys (pushover terminology) in the configuration file (copy `mqtt2pushover.conf.sample` to `mqtt2pushover.conf` for use). 

See details in the config sample for how to configure this script.
The path to the configuration file (which must be valid Python) is obtained from the `MQTT2PUSHOVERCONF` environment variable which defaults to `mqtt2pushover.conf`.

## Obligatory screenshot

![pushover on iOS](screenshot.png)

## Requirements

You'll need at least the following components:

* Python 2.x (tested with 2.6 and 2.7)
* An MQTT broker (e.g. [Mosquitto](http://mosquitto.org))
* The Paho Python module: `pip install paho-mqtt`

Depending on the notification services you wish to use, you'll also require one
or more of the following:

* A [pushover.net](https://pushover.net/) account
* A [Twitter](https://twitter.com) account with application keys
* NMA FIXME
* Prowl FIXME
* XBMC FIXME
* Mac OS X notification center: a Mac ;-) and code from FIXME

## Installation

```
mkdir /etc/mqtt2pushover/
git clone git://github.com/jpmens/mqtt2pushover.git /usr/local/mqtt2pushover/
cp /usr/local/mqtt2pushover/mqtt2pushover.conf.sample /etc/mqtt2pushover/mqtt2pushover.conf
cp /usr/local/mqtt2pushover/mqtt2pushover.init /etc/init.d/mqtt2pushover
update-rc.d mqtt2pushover defaults
cp /usr/local/mqtt2pushover/mqtt2pushover.default /etc/default/mqtt2pushover
Edit /etc/default/mqtt2pushover and /etc/mqtt2pushover/mqtt2pushover.conf to suit
chmod a+x /usr/local/mqtt2pushover/mqtt2pushover.py
chmod a+x /etc/init.d/mqtt2pushover`
/etc/init.d/mqtt2pushover start`
```
