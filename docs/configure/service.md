(configure-service)=
(services)=
# Services

## Introduction

This section of the documentation will outline how to configure mqttwarn
services. Services are instances of service plugins, using Python modules to
implement notifier components.

Later, you will learn how to subscribe to MQTT [topics](#topics), and map them
to the [services](#services) you have defined here.

You can choose from a variety of [](#notification-services), or you can write
your own notification plugin easily, see [](#custom-notification-plugins).


## Configuration

Configuration sections called `[config:xxx]` configure settings for a service,
where `xxx` is the name of the service. When a service is launched, a corresponding
section is mandatory to be present in the mqttwarn configuration file.

{#service-targets}
A service configuration section has a mandatory option called `targets`, which is
used to define groups of multiple recipients or targets. It is expected to be a
dictionary, where each item defines an individual service point for a particular
service.

The keys are _target names_, and the structure and value depends on what the
particular service plugin implementation expects.

The original configuration variant, still used by many service plugins, looks like this.
```ini
[config:xxx]
targets = {
    'targetname1': [ 'address1', 'address2' ],
    'targetname2': [ 'address3', 'address4' ],
  }
```

:::{note}
Historically, as outlined in the example above, the value / right-hand side of the
recipient/target group map, was exclusively defined as a `list`, and as such, the
term _address list_ was used.

Nowadays, after a few evolution cycles of mqttwarn, the value can have a different
data type and structure, depending on the particular service plugin. As such, the
term _target address descriptor_ is used now.

For example, after implementing [named target address descriptor options], the
configuration of the [Pushsafer service plugin](#pushsafer) is much more capable now.
```ini
[config:pushsafer]
targets = {
    'basic': { 'private_key': '3SAz1a2iTYsh19eXIMiO' },
    'extraphone': { 'private_key': '3SAz1a2iTYsh19eXIMiO', 'time_to_live': 60, 'priority': 2, 'retry': 60, 'expire': 600, 'answer': 0 }
    }
```
:::

Other than the mandatory `targets` option, and an optional `module` option, these sections
_may_ have more options. Some of them may even be _required_ for a particular service.

Effectively, this configuration snippet defines individual groups of "target addresses"
for a particular service, and assigns them "target names". Using those groups, it is, for
example, possible to define different...

- target paths for the `file` service.
- database tables for the `mysql` service.
- topic names for outgoing `mqtt` publishers.
- hostname/port number combinations for `xbmc`, etc.


## General options

Individual services offer different configuration options, however there are a
few settings optionally available to **all services**.

For example, the `decode_utf8` option, which is `True` by default, can be
turned off for a whole service definition. This makes it suitable to receive
and process binary or other non-UTF8 data.

```ini
# Don't assume incoming MQTT message to be encoded in UTF-8.
# This is applicable for receiving and processing binary data.
decode_utf8 = False
```


## Launching services

In order to launch configured services, you will have to add them to the global
`defaults` section of the `mqttwarn.ini` configuration file. For launching
multiple services, please use a comma-separated list.

```ini
[defaults]
launch = xxx, foo
```


## Module resolvement

### Resolving the name
The Python module name for the service will be determined...

{style=lower-alpha}
1. from the name of the definition itself. For `[config:xxx]`, it would be `xxx`. 
   ```ini
   [config:xxx]
   ```
2. from the value of the optional `module` option within that configuration
   section, when given.
   ```ini
   [config:custom-service]
   module = xxx
   ```

   :::{admonition} Note
   :class: note dropdown
   
   A service definition using the `module = xxx` variant will use the Python
   module `xxx`, however it has its own distinct set of service options. It is
   thus possible to have several service configurations for the same underlying
   service, with different configurations, e.g. one for files that should have
   notifications appended, and one for files that should get truncated before
   writes.
   
   #### Example
   
   Consider this configuration file in which we want two services of type log.
   We launch an additional `xxxlog` service here, also based on the `log` module.
   
   ```ini
   # Note how both services must be launched.
   [defaults]
   launch = log, xxxlog
   
   # Configure two individual services, both using the `log` module.
   [config:log]
   targets = {
     'debug'  : [ 'debug' ],
   }
   
   # Note how the xxxlog is instantiated from log.
   [config:xxxlog]
   module = log
   targets = {
     'debug'  : [ 'debug' ],
   }
   
   # The topic subscription rule using both services.
   [topic/1]
   targets = log:debug, xxxlog:debug
   ```
   :::


### Resolving the module
There are three options how the _module name_ will be resolved to a _Python module_.

1. When the module name is a plain string without a dot, and does not end with `.py`,
   it will be resolved to a module filename inside the built-in [mqttwarn/services] 
   directory.
2. When the module name contains a dot, and does not end with `.py`, it will be
   resolved as an absolute dotted reference to a Python module, see [](#load-service-from-package).
3. When the module name ends with a `.py` suffix, it will be treated as a 
   reference to a Python file, see [](#load-service-from-file).


(load-external-service)=
## Loading external services

In order to bring in custom sink components to `mqttwarn` in form of service
notification plugins, there are two options. We will explore them on behalf of
corresponding example configuration snippets.


(load-service-from-package)=
### From package

When the module name contains a dot, and does not end with `.py`, it will be
resolved as an absolute dotted reference using Python's [importlib](inv:python#library/importlib).
In this way, it is easy to load modules from other packages than mqttwarn.

This configuration snippet outlines how to load a custom plugin from a Python
module referenced in "dotted" notation. Modules will be searched for in all
directories listed in [`sys.path`], so any installed Python package will be
available. Additional directories can be added by using the [`PYTHONPATH`]
environment variable.

:::{admonition} Example
:class: note dropdown
```ini
[defaults]
; name the service providers you will be using.
launch = log, file, acme.foobar

[config:acme.foobar]
targets = {
    'default'  : [ 'default' ],
  }

[test/plugin-module]
; echo '{"name": "temperature", "value": 42.42}' | mosquitto_pub -h localhost -t test/plugin-module -l
targets = acme.foobar:default
format = {name}: {value}
```
:::


(load-service-from-file)=
### From file

When the module name ends with a `.py` suffix, it will be treated as a 
reference to a Python file. It can be either absolute, or relative to
the current working directory, or relative to the directory of the
configuration file.

This configuration snippet outlines how to load a custom plugin from a Python
file referenced by file name. When relative file names are given, they will be
resolved from the directory of the `mqttwarn.ini` file, which is, by default,
the `/etc/mqttwarn` folder.

:::{admonition} Example
:class: note dropdown
```ini
[defaults]
; name the service providers you will be using.
launch = log, file, acme/foobar.py

[config:acme/foobar.py]
targets = {
    'default'  : [ 'default' ],
  }

[test/plugin-file]
; echo '{"name": "temperature", "value": 42.42}' | mosquitto_pub -h localhost -t test/plugin-file -l
targets = acme/foobar.py:default
format = {name}: {value}
```
:::


(custom-notification-plugins)=
## Creating custom notification plugins

Creating new service plugins is easy, and we recommend you use the `file`
plugin as a blueprint and start from there.

Plugins are invoked with two arguments, `srv` and `item`. `srv` is an object
with some helper functions, and `item` a dictionary which contains information
on the message which is to be handled by the plugin. `item` has the following
top-level keys:

```python
item = {
    'service'       : 'string',       # Name of handling service (`twitter`, `file`, ...)
    'target'        : 'string',       # Name of target (`o1`, `janejol`) in service
    'addrs'         : list,           # List of addresses from SERVICE_targets
    'config'        : dict,           # None or dict from SERVICE_config {}
    'topic'         : 'string',       # MQTT topic the message was received on
    'payload'       : 'string',       # Raw message payload
    'message'       : 'string',       # Formatted message (if no format string, then equals payload)
    'data'          : None,           # Dictionary with transformation data
    'title'         : 'mqttwarn',     # Optional title from title{}
    'priority'      : 0,              # Optional priority from priority{}
}
```


[mqttwarn/services]: https://github.com/mqtt-tools/mqttwarn/tree/main/mqttwarn/services
[named target address descriptor options]: https://github.com/mqtt-tools/mqttwarn/issues/628
[`PYTHONPATH`]: https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH
[`sys.path`]: https://docs.python.org/3/library/sys.html#sys.path
