(owntracks-ntfy-recipe)=

# Forward OwnTracks low-battery warnings to ntfy


## About

By subscribing to your [OwnTracks] MQTT topic, and adding a user-defined filter
function, you can make `mqttwarn` send notifications, for example when your
phone battery level decreases below a certain threshold.


## Details

As an example, this tutorial will submit notifications to a public topic on
[ntfy.sh]. However, you can always choose a different notification service
provided by `mqttwarn`, or run your own instance of ntfy. A list of all options
is presented on the [](#notifier-catalog) page.

The tutorial will expect that you installed the `mqttwarn` command-line program
on your machine, so that you can run it within your terminal. There are different
options to [install mqttwarn](#install).


## Configuration

Within the mqttwarn configuration file, the `launch` setting within the
[](#configuration-defaults-section), and the `[config:ntfy]` [service section](#services)
will define ntfy as a notification target.

The [topic section](#topics) `[owntracks/#]` will define the MQTT topic mqttwarn will
subscribe to, here `owntracks/#`. Its configuration settings `filter`, `format`, and
`targets`, will instruct mqttwarn to format the outbound message like defined by a
template string, and dispatch it to the corresponding target address descriptor slot
`ntfy:testdrive`.

:::{literalinclude} mqttwarn-owntracks.ini
:language: ini
:::

The user-defined filter function `owntracks_batteryfilter()` will inspect OwnTracks'
JSON event payload for the value of your phone's battery level.

:::{literalinclude} mqttwarn-owntracks.py
:language: python
:::


## Usage

Using three terminal sessions, and one browser session, you can exercise the tutorial
interactively.

### Setup
First, let's start the [Mosquitto] MQTT broker.
```shell
docker run --name=mosquitto -it --rm --publish=1883:1883 eclipse-mosquitto:2.0 mosquitto -c /mosquitto-no-auth.conf
```

Let's acquire the configuration file `mqttwarn-owntracks.ini`, and the user-defined
functions file `mqttwarn-owntracks.py`, and start `mqttwarn`.
```shell
wget https://github.com/mqtt-tools/mqttwarn/raw/main/examples/owntracks-ntfy/mqttwarn-owntracks.ini
wget https://github.com/mqtt-tools/mqttwarn/raw/main/examples/owntracks-ntfy/mqttwarn-owntracks.py
mqttwarn --config-file=mqttwarn-owntracks.ini
```

Before dry-run publishing a JSON message, in order to validate your setup, subscribe to the
ntfy topic `testdrive`, either using your browser of choice,
```shell
open https://ntfy.sh/testdrive
```
or a commandline-based HTTP client like `curl`.
```shell
curl -s https://ntfy.sh/testdrive/json
```

### Self-test
Now, when publishing a minimal example JSON event payload, `mqttwarn` will run a notification
to ntfy when the battery level threshold is reached, as instructed.
```shell
echo '{"batt": 19}' | mosquitto_pub -t 'owntracks/testdrive' -l
```
![](https://user-images.githubusercontent.com/453543/236962377-65c7194c-79e7-4ea9-ad19-7ace0f58011f.png)
![](https://user-images.githubusercontent.com/453543/236970113-765274cd-24cb-4e87-9d5c-dd65aa8e8b42.png)

A JSON event with a battery level above the minimum threshold will **not** trigger a notification.
```shell
echo '{"batt": 42.42}' | mosquitto_pub -t 'owntracks/testdrive' -l
```
An invalid message, which can't be decoded, will also not trigger a notification.
```shell
echo 'foobar' | mosquitto_pub -t 'owntracks/testdrive' -l
```


## Appendix

This section demonstrates a few alternative methods for solving different aspects of this
recipe, and also includes administrative information.

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

### Backlog
:::{todo}
- [o] Define battery threshold level within the configuration file.
:::


[Mosquitto]: https://mosquitto.org
[ntfy.sh]: https://ntfy.sh/
[OwnTracks]: https://owntracks.org
