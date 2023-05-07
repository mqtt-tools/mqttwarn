(using-oci-image)=
# Using the OCI image with Docker or Podman

If you would rather use `mqttwarn` without installing Python and the required
libraries, you can run the OCI image on [Docker] or [Podman].

You can run mqttwarn as a service, i.e. in the background, or you can run it
interactively, perhaps to help diagnose a problem.

OCI images are available at:

- https://github.com/orgs/mqtt-tools/packages/container/package/mqttwarn-standard
- https://github.com/orgs/mqtt-tools/packages/container/package/mqttwarn-full

## Choosing the OCI image

Choose one of those OCI images.
```shell
# The standard image on GHCR.
export IMAGE=ghcr.io/mqtt-tools/mqttwarn-standard:latest

# The full image on GHCR.
export IMAGE=ghcr.io/mqtt-tools/mqttwarn-full:latest
```

## Interactively

In order to verify `mqttwarn` works appropriately with the current
configuration, you might want to invoke it interactively.

The following commands assume you start from scratch and will guide you through
the necessary steps needed to create a configuration and run it.

Within an empty folder, create a baseline `mqttwarn.ini` file:
```shell
docker run -it --rm --volume=$PWD:/etc/mqttwarn $IMAGE mqttwarn make-config > mqttwarn.ini
docker run -it --rm --volume=$PWD:/etc/mqttwarn $IMAGE mqttwarn make-udf > udf.py
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

Run the OCI image from anywhere by specifying a full path to the
configuration file:
```shell
--volume=/full/path/to/folder:/etc/mqttwarn
```

### Log file

By default, the log output will be sent to STDERR.
```ini
logfile   = stream://sys.stderr
```

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

*Warning:* By default, Docker will log everything, and it does not rotate or
clean itself.  When running under Docker daemon, add the following defaults
to your `/etc/docker/daemon.json` to control you logs:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

It also might be possible to add a `logging` entry to your individual `docker-compose.yml`
file for `mqttwarn`, rather than changing it at the system level:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    env: "os"
```



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
from the files on GitHub).

Execute the following from the root of the project :
```
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain

docker build --tag=local/mqttwarn-standard --file=Dockerfile .
```

```
docker build --tag=local/mqttwarn-full --file=Dockerfile.full .
```

You can then edit any files and rebuild the image as many times as you need. 
You don't need to commit any changes.

The name `local/mqttwarn-standard` is not meaningful, other than making it obvious when
you run it that you are using your own personal image. You can use any name you
like, but avoid `mqttwarn` otherwise it's easily confused with the official
images.


## Installing additional Python packages into OCI image

In order to use `mqttwarn` with additional Python modules not included in the
baseline image, you will need to build custom OCI images based on the
canonical `ghcr.io/mqtt-tools/mqttwarn-standard:latest`.

We prepared an example which outlines how this would work with the Slack SDK.
By using the `Dockerfile.mqttwarn-slack`, this command will build an OCI
image called `mqttwarn-slack`, which includes the Slack SDK:

```shell
docker build --tag=mqttwarn-slack --file=Dockerfile.mqttwarn-slack .
```

## The "full" image, including all dependencies

If you prefer not to fiddle with those details, but instead want to run a full
image including dependencies for all modules, we have you covered. Alongside
the standard image, there is also `ghcr.io/mqtt-tools/mqttwarn-full:latest`.

## Image sizes

We determined the **compressed** image sizes using [dockersize]::

    $ dockersize ghcr.io/mqtt-tools/mqttwarn-standard:latest
    linux/amd64   172.89M
    linux/arm64   167.12M
    linux/arm/v7  143.39M

    $ dockersize ghcr.io/mqtt-tools/mqttwarn-full:latest
    linux/amd64   205.96M
    linux/arm64   186.81M
    linux/arm/v7  160.47M


[dockersize]: https://gist.github.com/MichaelSimons/fb588539dcefd9b5fdf45ba04c302db6?permalink_comment_id=4243739#gistcomment-4243739
[Docker]: https://docker.com/
[Podman]: https://podman.io/
