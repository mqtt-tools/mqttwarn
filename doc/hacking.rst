*******
Hacking
*******
For hacking on mqttwarn, please install it in development mode.

Get hold of the sources::

    git clone https://github.com/jpmens/mqttwarn
    cd mqttwarn
    git checkout develop

Create virtualenv::

    virtualenv .venv2
    source .venv2/bin/activate

Install Python package in development mode::

    python setup.py develop

Install extras::

    pip install --editable .[xmpp]

You can also add multiple extras, all at once::

    pip install --editable .[asterisk,nsca,osxnotify,tootpaste,xmpp]
