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

Install extras::

    source .venv/bin/activate
    pip install --editable=.[xmpp]

You can also add multiple extras, all at once::

    pip install --editable=.[asterisk,nsca,osxnotify,tootpaste,xmpp]


************
Using VSCode
************

To install the free, non-telemetry version of Microsoft VSCode::

    brew install --cask vscodium

This project includes a launch configuration file ``.vscode/launch.json``.
After installing the ``mqttwarn`` development sandbox into a virtualenv, for
example by invoking ``make test``, VSCode will automatically detect it and
will be able to launch the ``mqttwarn`` entrypoint without further ado.

Otherwise, setup the virtualenv manually by invoking those commands::

    python3 -m venv .venv
    source .venv/bin/activate
    pip install --editable=.[test] --upgrade
