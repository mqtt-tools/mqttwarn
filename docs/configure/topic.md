(configure-topic)=
(topics)=
# Topics

## Introduction

This section of the documentation will outline how to configure mqttwarn 
topics. You will learn how to subscribe to MQTT [topics](#topics), and map 
them to the [services](#services) you have defined.

mqttwarn's topic configuration subsystem relates 1:1 to MQTT's topics. You will
configure topic subscriptions in the same way you are used to, using the same
wildcard scheme you are already accustomed to, for example when using [`mosquitto_pub`].


## The `[__topic__]` sections

All sections not called `[defaults]` or `[config:xxx]` are treated as MQTT topics
to subscribe to. _mqttwarn_ handles each message received on this subscription
by handing it off to one or more [service targets](#service-targets).

Section names must be unique and must specify the name of the topic to be processed. 
If the section block does not have a `topic` option, then the section name will be used.

When a message is received at a topic with more than one matching sections, it
will be directed to the targets in all matching sections.  For consistency,
it's a good practice to explicitly provide `topic` options to all such sections.

{#topic-options}
A section can have additional mandatory (`M`) or optional (`O`) options:

| Option        |  M/O   | Description                                    |
| ------------- | :----: | ---------------------------------------------- |
| `targets`     |   M    | service targets for this SUB                   |
| `topic`       |   O    | topic to subscribe to (overrides section name) |
| `filter`      |   O    | function name to suppress this msg             |
| `datamap`     |   O    | function name parse topic name to dict         |
| `alldata`     |   O    | function to merge topic, and payload with more |
| `format`      |   O    | function or string format for output           |
| `priority`    |   O    | used by certain targets (see below). May be func()  |
| `title`       |   O    | used by certain targets (see below). May be func()  |
| `image`       |   O    | used by certain targets (see below). May be func()  |
| `template`    |   O    | use Jinja2 template instead of `format`        |
| `qos`         |   O    | MQTT QoS for subscription (dflt: 0)            |


## Basic message routing

Consider the following example configuration.

```ini
[icinga/+/+]
targets = log:info, file:f01, mysql:nagios

[my/special]
targets = mysql:m1, log:info

[my-other-special]
topic = another/topic
targets = log:debug
```

- MQTT messages received at `icinga/+/+` will be directed to the three specified
  targets.
- Messages received at `my/special` will be stored in a `mysql` target and will 
  be logged at level "INFO".
- Messages received at `another/topic` (not at `my-other-special`) will be logged 
  at level "DEBUG".


## Advanced message routing


### Dictionary targets

Targets can also be defined as a dictionary, containing items of `{topic: targets}`. 
In that case, message matching the section can be dispatched in more  flexible ways 
to selected targets. Consider the following example:

```ini
[#]
targets = {
  '/#': 'file:0',
  '/test/#': 'file:1',
  '/test/out/#': 'file:2',
  '/test/out/+': 'file:3',
  '/test/out/+/+': 'file:4',
  '/test/out/+/state': 'file:5',
  '/test/out/FL_power_consumption/state': [ 'file:6', 'file:7' ],
  '/test/out/BR_ambient_power_sensor/state': 'file:8',
  }
```

With such a message dispatching configuration, the message is dispatched to the
targets matching the most specific topic.

- If the message is received at `/test/out/FL_power_consumption/state`, it will
  be directed to `file:6` and `file:7` targets only.
- A message received at `/test/out/AR_lamp/state` will be directed to `file:5`.
- A message received at `/test/out/AR_lamp/command` will go to `file:4`.

The dispatcher mechanism is always trying to find the most specific match. It
allows to define the wide topic with default targets while some more specific 
topics can be handled differently. It gives additional flexibility in message 
routing.

:::{attention}
The closing brace `}` of the `targets` dictionary MUST be indented. This is an
artifact of Python's [ConfigParser](inv:python#library/configparser).
:::


### Templated targets

By defining topic targets as templates, and interpolating transformation data,
we can make _mqttwarn_ dispatch messages dynamically, based on the values of
the transformation data dictionary.

By bundling multiple target rules into a single templated one, this may save a
few explicit rules to be configured within your [topic section](#topics) definitions.

#### Example 1
To get an idea about how this works, let's define the placeholder variable
`loglevel` inside the `targets` option of a topic section.
```ini
[topic-targets-dynamic]
topic   = test/topic-targets-dynamic
format  = Something {loglevel} happened! {message}
targets = log:{loglevel}
```

When sending this value through a JSON encoded message or by computing it
through the `alldata` transformation machinery, it will get interpolated into
the designated topic target. Example:
```shell
mosquitto_pub \
  -t test/topic-targets-dynamic \
  -m '{"loglevel": "crit", "message": "Nur Döner macht schöner!"}'
```

This will issue the following message into the log file:
```text
2016-02-14 18:09:34,822 CRITICAL [log] Something crit happened! Nur Döner macht schöner!
```

While this little example might feel artificial, there are more sensible use
cases like determining the recipient address of `smtp` or `xmpp` receivers by
interpolating information from topic names or message payloads.
Please have a look at how to [incorporate topic names into topic targets] for a
more meaningful example in this regard.


#### Example 2

The [](#processing-frigate-events) tutorial used a configuration snippet like this.
```ini
[frigate/cam1/goat/snapshot]
targets = store-image:cam1-goat
[frigate/cam2/squirrel/snapshot]
targets = store-image:cam2-squirrel
```

Using [](#templated-targets), this can be condensed like this, not needing to
repeat each and every slot to be addressed. Of course, it needs a corresponding
[](#decoding) function to propagate the `camera` and `label` values into the
transformation data.
```ini
[frigate/+/+/snapshot]
targets = store-image:{camera}-{label}
```


[incorporate topic names into topic targets]: https://github.com/mqtt-tools/mqttwarn/wiki/Incorporating-topic-names#incorporate-topic-names-into-topic-targets
[`mosquitto_pub`]: https://mosquitto.org/man/mosquitto_pub-1.html
