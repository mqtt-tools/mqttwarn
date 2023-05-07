{#mqtt-media-player}
# Simple MQTT media player


## About

The idea is to implement a simple MQTT media player on Linux, which can be used to play TTS
messages from Home Assistant. Home Assistant renders the TTS stream as an MP3 and makes it
available on its HTTP server, so a corresponding command using `mplayer` to play the audio
resource would look like this.
```shell
mplayer -volume 80 http://home.assistant.address:8123/api/tts_proxy/6a0efdf280bf8c79a.mp3
```

## Configuration

The solution for this will be implemented using mqttwarn's [](#execute) service plugin, which
can be used to invoke programs, and interpolate MQTT payload data.

:::{literalinclude} mqttwarn-mplayer.ini
:language: ini
:::


## Usage
Using three terminal sessions, you can exercise the example interactively. First, let's start
the [Mosquitto] MQTT broker.
```shell
docker run --name=mosquitto -it --rm --publish=1883:1883 eclipse-mosquitto:2.0 mosquitto -c /mosquitto-no-auth.conf
```
Let's acquire the `mqttwarn-mplayer.ini` configuration file, and start `mqttwarn`.
```shell
wget https://github.com/mqtt-tools/mqttwarn/raw/main/examples/mediaplayer/mqttwarn-mplayer.ini
mqttwarn --config-file=mqttwarn-mplayer.ini
```
Now, when publishing the URL to the audio resource on the designated MQTT topic, `mqttwarn` will
invoke the `mplayer` command as instructed. 
```shell
echo 'http://home.assistant.address:8123/api/tts_proxy/6a0efdf280bf8c79a.mp3' | \
  mosquitto_pub -t 'mediaplayer/play' -l
```


[Home Assistant]: https://www.home-assistant.io/
[Mosquitto]: https://mosquitto.org
