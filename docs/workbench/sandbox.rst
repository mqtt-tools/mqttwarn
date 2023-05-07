.. _sandbox:

############################
mqttwarn development sandbox
############################


************
Installation
************

For hacking on mqttwarn, please install it in development mode.

Get hold of the sources, initialize a Python virtualenv, and run the software tests::

    git clone https://github.com/mqtt-tools/mqttwarn
    cd mqttwarn
    make test

Install extras::

    source .venv/bin/activate
    pip install --editable=.[xmpp]

You can also add multiple extras, all at once::

    pip install --editable=.[asterisk,nsca,desktopnotify,tootpaste,xmpp]


**************
Software tests
**************

Invoke software tests::

    make test

Run individual test cases. For example, to run all "end-to-end" test cases, and
turn off coverage reporting, invoke::

    source .venv/bin/activate
    pytest --no-cov -k e2e

Display and browse code coverage results in HTML format::

    open .pytest_results/htmlcov/index.html



*************
Documentation
*************

The mqttwarn documentation is written in `reStructuredText`_ and `Markdown`_,
and is rendered using `Sphinx`_ and `MyST`_.

MyST, a rich and extensible flavour of `Markdown`_, is a superset of the
`CommonMark syntax specification`_. It adds features focussed on scientific and
technical documentation authoring. The Markedly Structured Text Parser is a Sphinx
and Docutils extension to parse MyST.

Build and view the documentation::

    make docs-autobuild

For learning about how to link to references within Markdown documents, please
read the `MyST Cross-references`_ documentation.


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


.. _CommonMark syntax specification: https://spec.commonmark.org/
.. _Markdown: https://en.wikipedia.org/wiki/Markdown
.. _MyST: https://myst-parser.readthedocs.io/
.. _MyST Cross-references: https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html
.. _reStructuredText: https://en.wikipedia.org/wiki/ReStructuredText
.. _Sphinx: https://www.sphinx-doc.org/
