############################
mqttwarn development sandbox
############################


*******
Hacking
*******
For hacking on mqttwarn, please install it in development mode.

Get hold of the sources::

    git clone https://github.com/jpmens/mqttwarn
    cd mqttwarn

Invoke software tests::

    make test

Invoke software tests, with coverage::

    make test-coverage

Install extras::

    source .venv/bin/activate
    pip install --editable=.[xmpp]

You can also add multiple extras, all at once::

    pip install --editable=.[asterisk,nsca,desktopnotify,tootpaste,xmpp]

Build the documentation::

    make docs-html
    open docs/_build/html/index.html


************
Using VSCode
************

For installing the free, non-telemetry version of Microsoft VSCode, invoke::

    brew install --cask vscodium

This project includes a launch configuration file ``.vscode/launch.json``.
After installing the ``mqttwarn`` development sandbox into a virtualenv, for
example by invoking ``make test``, VSCode will automatically detect it and
will be able to launch the ``mqttwarn`` entrypoint without further ado.

Otherwise, setup the virtualenv manually by invoking those commands::

    # On Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # On Windows
    python -m venv .venv
    .venv/Scripts/activate

    pip install --editable=.[test] --upgrade

For properly configuring a virtualenv, please also read those fine resources:

- https://code.visualstudio.com/docs/python/environments
- https://medium.com/@kylehayes/using-a-python-virtualenv-environment-with-vscode-b5f057f44c6a
