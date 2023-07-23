(configure-overview)=
(mqttwarn.ini)=
# `mqttwarn.ini` at a glance

## Getting started

The authors recommend you start off with a simple configuration, which will log 
messages received on the MQTT topic `test/+`, and additionally write them to a
file. For example, use the following configuration file as a blueprint and save
it into a file `mqttwarn.ini`.

```ini
[defaults]

; MQTT broker address.
hostname  = 'localhost'
port      = 1883

; Names of the service providers to activate.
launch	  = file, log

[config:file]
append_newline = True
targets = {
  'mylog': ['/tmp/mqtt.log']
  }

[config:log]
targets = {
  'info': [ 'info' ]
}

[test/+]
targets = file:mylog, log:info
```

:::{attention}
The closing brace `}` of the `targets` dictionary MUST be indented. This is an
artifact of Python's [ConfigParser](inv:python#library/configparser).
:::

Launch the `mqttwarn` program, and keep an eye on its log file, which is 
`mqttwarn.log` by default. Then, publish two MQTT messages so they will be
picked up by mqttwarn, for example using `mosquitto_pub`.
```
mosquitto_pub -t test/1 -m "Hello"
mosquitto_pub -t test/name -m '{ "name" : "Jane" }'
```

After that, the output file `/tmp/mqtt.log` should contain the payload of both
messages:
```shell
cat /tmp/mqtt.log
Hello
{ "name" : "Jane" }
```

Stop _mqttwarn_, and add the following line to the `[test/+]` section:
```ini
format = -->{name}<--
```

What we are configuring _mqttwarn_ to do here, is to try and decode the incoming
JSON payload and format the output in such a way as that the JSON `name` element 
is copied to the output (surrounded with a bit of sugar to illustrate the fact 
that we can output whatever text we want).

If you repeat to publish of the second message, you should see the following in
your output file `/tmp/mqtt.log`:
```text
-->Jane<--
```

(configuration-defaults-section)=
## The `[defaults]` section

Most of the options in the configuration file have sensible defaults, and/or ought to be self-explanatory:

```ini
[defaults]
hostname     = 'localhost'         ; default
port         = 1883
username     = None
password     = None
clientid     = 'mqttwarn'
lwt          = 'clients/mqttwarn'
lwt_alive    = '1'
lwt_dead     = '0'
skipretained = True
cleansession = False

; logging

; Log format
logformat = '%(asctime)-15s %(levelname)-5s [%(module)s] %(message)s'

; Send log to STDERR (default)
logfile   = 'stream://sys.stderr'

; Write log output to file
; logfile   = 'mqttwarn.log'

; Turn off logging completely
; logfile   = false

; one of: CRITICAL, DEBUG, ERROR, INFO, WARN
loglevel     = DEBUG

; optionally set the log level for filtered messages, defaults to INFO
; filteredmessagesloglevel = DEBUG

; path to file containing self-defined functions like `format` or `alldata`
functions = 'myfuncs.py'

; name the service providers you will be using.
launch   = file, log, desktopnotify, mysql, smtp

; Publish mqttwarn status information (retained)
status_publish = True
; status_topic = mqttwarn/$SYS


; optional: TLS parameters. (Don't forget to set the port number for
; TLS (probably 8883).
; You will need to set at least `ca_certs' if you want TLS support and
; tls = True
; ca_certs: path to the Certificate Authority certificate file (concatenated
;           PEM file)
; tls_version: currently one of 'tlsv1_1', 'tlsv1_2' (or 'sslv3', 'tlsv1' deprecated)
; tls_insecure: True or False (False is default): Do or do not verify
;               broker's certificate CN
; certfile: path to PEM encode client certificate file
; keyfile: path to PEM encode client private key file
tls = True
ca_certs = '/path/to/ca-certs.pem'
certfile = '/path/to/client.crt'
keyfile = '/path/to/client.key'
tls_version = 'tlsv1'
tls_insecure = False

```

### `functions`

The `functions` option specifies the path to a Python file containing functions you use in formatting or filtering data (see below). The `.py` extension to the path name you configure here must be specified.

### `launch`

In the `launch` option you specify a list of comma-separated _service_ names  
defined within the `[config:xxx]` sections which should be launched.

You should launch every service you want to use from your topic/target definitions here.

### `status_publish`

Like with Mosquitto's `$SYS` topic, `mqttwarn` can publish status information to the broker.
This is useful for automated updates (Docker Swarm, Watchtower, etc.).

To enable status information publishing, configure `status_publish = True`. The other option,
`status_topic`, defaults to `status_topic = mqttwarn/$SYS`.
The messages will be published with the `retained` flag.

For example:
```
root@mymachine:~$ mosquitto_sub -t 'mqttwarn/$SYS/#' -v
mqttwarn/$SYS/version 0.26.2
mqttwarn/$SYS/platform darwin
mqttwarn/$SYS/python/version 3.9.7
```

## Service sections

The anatomy of a `[config:xxx]` service configuration snippet is:
```ini
[config:xxx]
targets = {
    'targetname1': [ 'address1', 'address2' ],
    'targetname2': [ 'address3', 'address4' ],
  }
```

Please find [detailed information about the `[config:xxx]` sections](#configure-service)
on a dedicated documentation page.

## Topic sections

The anatomy of a `[__topic__]` configuration snippet is:

```ini
[icinga/+/+]
targets = log:info, file:f01, mysql:nagios
```

Please find [detailed information about the `[__topic__]` sections](#configure-topic)
on a dedicated documentation page.

## Transformation options

Please find [detailed information about how to configure transformations](#configure-transformation)
on a dedicated documentation page.

## The `[failover]` section

There is a special section called `[failover]` for defining one or multiple
targets for internal error conditions. Currently, there is only one error 
handled by this logic, which is "broker disconnection". The configuration is
completely optional.

This allows you to set up a target for receiving errors generated within 
_mqttwarn_. The message is handled like any other with an error code passed as 
the `topic` and the error details as the `message`. You can use formatting and 
transformations as well as filters, just like any other [topic](#topics).

This is an example which will log any failover events to an error log, and 
display them on all XBMC targets:
```ini
[failover]
targets  = log:error, xbmc
title    = mqttwarn
```

## Variables

You can load option values either from environment variables or file content.
To do this, replace option's value with one of the following:

- `${ENV:FOO}` - Replaces option's value with environment variable `FOO`.
- `${FILE:/path/to/foo.txt}` - Replaces option's value with file contents from
  `/path/to/foo.txt`. The file path can also be relative like `${FILE:foo.txt}`
  in which case the file is loaded relative to configuration file's location.

The variable pattern can take either form like `$TYPE:NAME` or `${TYPE:NAME}`.
Latter pattern is required when variable name (`NAME`) contains characters that
are not alphanumeric or underscore.

For example:
```ini
[defaults]
username = $ENV:MQTTWARN_USERNAME
password = $ENV:MQTTWARN_PASSWORD

[config:xxx]
targets = {
    'targetname1': [ '${FILE:/run/secrets/address.txt}' ],
  }
```
