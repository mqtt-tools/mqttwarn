(using-freebsd)=
# Installing mqttwarn on FreeBSD

With this installation method about how to install mqttwarn on [FreeBSD],
you will acquire the [py-mqttwarn] package from the [FreeBSD ports tree],
and install it on your machine.

## Synopsis

```bash
pkg install sysutils/py-mqttwarn
```


## Additional service plugins

In order to add support for a specific service plugin not bundled with the
default installation, you will need to install its dependencies manually.

In order to do that, head over to the [`setup.py`] file of mqttwarn, inspect
the list of dependencies, and use the [FreshPorts search] to figure out the
package name of the corresponding dependency on the FreeBSD ports tree,
for example [py-pyserial] or [py-slixmpp]. Then, install the additional
package(s) using [pkg], for example:
```
pkg install comms/py-pyserial
pkg install net-im/py-slixmpp
```

If some package is not available there, you may consider installing it from
the [Python package index] using `pip install <package>`, for example:
```
pip install pyserial slixmpp
```


[FreeBSD]: https://www.freebsd.org/
[FreeBSD ports tree]: https://www.freebsd.org/ports/
[FreshPorts search]: https://www.freshports.org/search.php
[pkg]: https://man.freebsd.org/cgi/man.cgi?query=pkg
[py-mqttwarn]: https://www.freshports.org/sysutils/py-mqttwarn/
[py-pyserial]: https://www.freshports.org/comms/py-pyserial/
[py-slixmpp]: https://www.freshports.org/net-im/py-slixmpp/
[Python package index]: https://pypi.org/
[`setup.py`]: https://github.com/mqtt-tools/mqttwarn/blob/main/setup.py
