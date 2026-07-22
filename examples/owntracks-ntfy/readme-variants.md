---
orphan: true
---

(owntracks-ntfy-variants)=

# OwnTracks-to-ntfy setup variants


## About

This section informs you about additional configuration and operation variants of the
[](#owntracks-ntfy-recipe) recipe. For example, you may want to use Docker or Podman
to run both mqttwarn and ntfy, or you may want to use another language than Python to
implement your filtering function.


## Docker and Podman

### Running mqttwarn as container
This command will run mqttwarn in a container, using the `docker` command to launch it.
Alternatively, `podman` can be used. It expects an MQTT broker to be running on `localhost`,
so it uses the `--network=host` option. The command will mount the configuration file and
the user-defined functions file correctly, and will invoke mqttwarn with the corresponding
`--config-file` option.
```shell
docker run --rm -it --network=host --volume=$PWD:/etc/mqttwarn \
  ghcr.io/jpmens/mqttwarn-standard \
  mqttwarn --config-file=mqttwarn-owntracks.ini
```

### Running ntfy as container
While this tutorial uses the ntfy service at ntfy.sh, it is possible to run your own
instance. For example, use Docker or Podman.
```shell
docker run --name=ntfy --rm -it --publish=5555:80 \
  binwiederhier/ntfy serve --base-url="http://localhost:5555"
```
In this case, please adjust the ntfy configuration section `[config:ntfy]` to use
a different URL, and make sure to restart mqttwarn afterwards.
```ini
[config:ntfy]
targets   = {'testdrive': 'http://localhost:5555/testdrive'}
```


(owntracks-ntfy-variants-udf)=

## Alternative languages for user-defined functions

### JavaScript

In order to try that on the OwnTracks-to-ntfy example, use the alternative
`mqttwarn-owntracks.js` implementation by adjusting the `functions` setting within the
`[defaults]` section of your configuration file, and restart mqttwarn.
```ini
[defaults]
functions = mqttwarn-owntracks.js
```

The JavaScript function `owntracks_batteryfilter()` implements the same rule as the
previous one, which was written in Python.

:::{literalinclude} mqttwarn-owntracks.js
:language: javascript
:::

:::{attention}
The feature to run JavaScript code is currently considered to be experimental.
Please use it responsibly.
:::
