# Running mqttwarn with Docker

If you would rather use `mqttwarn` without installing Python and the
required libraries, you can run it as a [Docker container](https://www.docker.com/).
You need to install only the Docker executable.

You can run the image as a service, i.e. in the background, or you can 
run it interactively, perhaps to help diagnose a problem.

Docker images are automatically published to:

- https://hub.docker.com/r/jpmens/mqttwarn
- https://github.com/orgs/jpmens/packages/container/package/mqttwarn-standard
- https://github.com/orgs/jpmens/packages/container/package/mqttwarn-full

## Choosing the Docker image

Choose one of those Docker images.
```shell
# The standard image on Docker Hub.
export IMAGE=jpmens/mqttwarn

# The standard image on GHCR.
export IMAGE=ghcr.io/jpmens/mqttwarn-standard:latest

# The full image on GHCR.
export IMAGE=ghcr.io/jpmens/mqttwarn-full:latest
```

## Interactively

In order to verify `mqttwarn` works appropriately with the current
configuration, you might want to invoke it interactively.

The following commands assume you start from scratch and will guide you through
the necessary steps needed to create a configuration and run it.

Within an empty folder, create a baseline `mqttwarn.ini` file:
```shell
docker run -it --rm --volume=$PWD:/etc/mqttwarn $IMAGE mqttwarn make-config > mqttwarn.ini
docker run -it --rm --volume=$PWD:/etc/mqttwarn $IMAGE mqttwarn make-samplefuncs > samplefuncs.py
```

Then, assuming your MQTT broker runs on `localhost`, amend the `mqttwarn.ini` like:
```ini
hostname     = 'host.docker.internal'
```

Now, invoke `mqttwarn`:
```shell
docker run -it --rm --volume=$PWD:/etc/mqttwarn $IMAGE
```

`Ctrl-C` will stop it. You can start and stop it as often as you like, here,
probably editing the `.ini` file as you go.

Note that you can run a local copy of the image, if you've built one (see below),
by replacing `$IMAGE` with `mqttwarn-local` in the following examples.


## As a service

This is the typical way of running `mqttwarn`.

From the folder containing your `mqttwarn.ini` file, run `mqttwarn` in the
background:
```shell
docker run --name=mqttwarn --detach --rm --volume=$PWD:/etc/mqttwarn $IMAGE
```

Follow the log:
```shell
docker logs mqttwarn --follow
```

To stop the container:
```shell
docker stop mqttwarn
```


## Options

### Configuration Location

Run the Docker image from anywhere by specifying a full path to the
configuration file:
```shell
--volume=/full/path/to/folder:/etc/mqttwarn
```

### Log file

By default, the log output will be sent to STDERR.

If you would like to log to a file on the host instead, add this to your
`mqttwarn.ini` file:
```ini
logfile = '/log/mqttwarn.log'
```
Add this argument to `docker run`:
```shell
--volume=$PWD/log:/log
```

`mqttwarn.log` will be created in your current folder, and appended to each
time the container is executed. You can delete the file between subsequent
invocations.


### If your MQTT Broker is also running in Docker on the same host

If you give the MQTT broker container a name, then you can refer to it by name rather than by
IP address. For instance, if it's named `mosquitto`, and started like
```shell
docker run --name=mosquitto -it --rm eclipse-mosquitto:1.6
docker run --name=mosquitto -it --rm eclipse-mosquitto:2.0 mosquitto -c /mosquitto-no-auth.conf
```
put this in your `mqttwarn.ini` file:
```ini
hostname  = 'mosquitto'
```
Then add this argument to `docker run`:
```shell
--link=mosquitto
```


### A full example

```shell
docker run -it --rm --volume=$PWD:/etc/mqttwarn --link=mosquitto $IMAGE
```


## Build the image

If you are making any changes to the `mqttwarn` application or to the
`Dockerfile`, you can build a local image from the files on your drive (not
from the files on Github).

Execute the following from the root of the project :
```
docker build -t mqttwarn-local .
```

You can then edit any files and rebuild the image as many times as you need. 
You don't need to commit any changes.

The name `mqttwarn-local` is not meaningful, other than making it obvious when
you run it that you are using your own personal image. You can use any name you
like, but avoid `mqttwarn` otherwise it's easily confused with the official
images.


## Installing additional Python packages into Docker image

In order to use `mqttwarn` with additional Python modules not included in the
baseline image, you will need to build custom Docker images based on the
canonical `jpmens/mqttwarn`.

We prepared an example which outlines how this would work with the Slack SDK.
By using the `Dockerfile.mqttwarn-slack`, this command will build a Docker
image called `mqttwarn-slack`, which includes the Slack SDK:

```shell
docker build --tag=mqttwarn-slack --file=Dockerfile.mqttwarn-slack .
```
