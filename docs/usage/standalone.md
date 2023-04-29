(using-standalone)=
# Running notification plugins standalone


## About

Using the `mqttwarn` command, you can invoke an individual notification plugin
directly, without the dispatching and transformation machinery, and without
needing to start it as a service.

This can be used for custom notification programs, and for debugging them,
without needing to exercise a full end-to-end MQTT publishing workflow.


## Details

To launch a plugin standalone, the commands in the next sections will give you an
idea how to pass relevant information on the command line. Please note that all
configuration options are obtained as strings in JSON format.

Many plugins will work without a configuration, and only need an `--options`
parameter. Others will need an additional baseline configuration, obtained per
`--config` parameter. Alternatively, a path to the configuration file can be
specified using the `--config-file` parameter.


## Synopsis

Launch `log` service plugin with a few target address descriptor options.
```shell
mqttwarn --plugin=log --options='{"message": "Hello world", "addrs": ["crit"]}'
```

:::{tip}
For producing JSON with command line / script programs, you can use the excellent
[jo] program, so you will not have to fiddle with curly braces and quotes too much.
```shell
mqttwarn --plugin=log --options="$(jo message="Hello world" addrs=$(jo -a crit))"
```
:::


## Examples

The best way to learn about this feature, is on behalf of a few more example invocations.

Invoke plugins that do not need a configuration, like `log`, `file`, or `pushover`.
```shell
# Launch "file" service plugin
mqttwarn --plugin=file --options='{"message": "Hello world\n", "addrs": ["/tmp/mqttwarn.err"]}'

# Launch "pushover" service plugin
mqttwarn --plugin=pushover --options='{"title": "About", "message": "Hello world", "addrs": ["userkey", "token"], "priority": 6}'
```

Invoke plugins that require a configuration, like `ssh`.
```shell
# Launch "ssh" service plugin
mqttwarn --plugin=ssh --config='{"host": "ssh.example.org", "port": 22, "user": "foo", "password": "bar"}' --options='{"addrs": ["command with substitution %s"], "payload": "{\"args\": \"192.168.0.1\"}"}'
```

Invoke `ntfy` plugin.
```shell
# Launch "ntfy" service plugin
mqttwarn --plugin=ntfy --options='{"addrs": {"url": "http://localhost:5555/testdrive"}, "title": "Example notification", "message": "Hello world"}' --data='{"tags": "foo,bar,äöü", "priority": "high"}'

# Launch "ntfy" service plugin, and add remote attachment
mqttwarn --plugin=ntfy --options='{"addrs": {"url": "http://localhost:5555/testdrive"}, "title": "Example notification", "message": "Hello world"}' --data='{"attach": "https://unsplash.com/photos/spdQ1dVuIHw/download?w=320", "filename": "goat.jpg"}'

# Launch "ntfy" service plugin, and add attachment from local filesystem
mqttwarn --plugin=ntfy --options='{"addrs": {"url": "http://localhost:5555/testdrive", "file": "goat.jpg"}, "title": "Example notification", "message": "Hello world"}'
```

Invoke external plugin.
```shell
# Launch "cloudflare_zone" service plugin from "mqttwarn-contrib"
pip install mqttwarn-contrib
mqttwarn --plugin=mqttwarn_contrib.services.cloudflare_zone --config='{"auth-email": "foo", "auth-key": "bar"}' --options='{"addrs": ["0815", "www.example.org", ""], "message": "192.168.0.1"}'
```


[jo]: https://github.com/jpmens/jo
