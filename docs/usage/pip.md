(using-pip)=
# Installing mqttwarn with pip

With this installation method, you will acquire a package of mqttwarn from PyPI
and install it on your workstation. We recommend to use a Python virtualenv for
that.

## Synopsis

```bash
pip install --upgrade mqttwarn
```

Add JavaScript support for user-defined functions.
```bash
pip install --upgrade 'mqttwarn[javascript]'
```

You can also add support for a specific service plugin.

```bash
pip install --upgrade 'mqttwarn[xmpp]'
```

You can also add support for multiple services, all at once.

```bash
pip install --upgrade 'mqttwarn[apprise,asterisk,nsca,desktopnotify,tootpaste,xmpp]'
```
