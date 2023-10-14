# -*- coding: utf-8 -*-
# (c) 2014-2023 The mqttwarn developers
import os
import platform
import sys

from setuptools import find_packages, setup
from versioningit import get_cmdclasses

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

requires = [
    "attrs<23",
    "docopt<1",
    "funcy<3",
    "future>=0.18.0,<1",
    "importlib-metadata; python_version<'3.8'",
    "importlib-resources; python_version<'3.8'",
    "jinja2<4",
    "paho-mqtt<2",
    "requests<3",
    "six<2",
]

extras = {
    "amqp": [
        "puka>=0.0.7; python_version<'3.12'",
    ],
    "apns": [
        "apns>=2.0.1",
    ],
    "apprise": [
        "apprise>=1.3,<2",
    ],
    "asterisk": [
        "pyst2>=0.5.0",
    ],
    "celery": [
        "celery",
    ],
    "chromecast": [
        "pychromecast>=7.5.0; python_version>='3.7'",
    ],
    "dnsupdate": [
        "dnspython>=1.15.0",
    ],
    "fbchat": [
        "fbchat>=1.3.6",
    ],
    "gss2": [
        "google-api-python-client<2; python_version>='3.7'",
        "gspread>=2.1.1",
        "oauth2client>=4.1.2",
    ],
    "mysql": [
        "mysql",
    ],
    "mysql_dynamic": [
        "mysqlclient",
    ],
    "nsca": [
        "pynsca>=1.6",
    ],
    "desktopnotify": [
        "desktop-notifier<4",
    ],
    "pastebinpub": [
        "Pastebin>=1.1.2",
    ],
    "postgres": [
        "psycopg2-binary>=2.7.4",
    ],
    "prowl": [
        "pyprowl>=3.0.1",
    ],
    "pushbullet": [
        # TODO: Upstream `send_note` utility function.
        # "pushbullet-python<2",
    ],
    "redispub": [
        "redis>=2.10.6",
    ],
    "rrdtool": [
        "rrdtool>=0.1.12",
    ],
    "serial": [
        "pyserial>=3.4",
    ],
    "slack": [
        "slack-sdk>=3.1.0",
    ],
    "ssh": [
        "paramiko>=2.4.1; python_version>='3.7'",
    ],
    "tootpaste": [
        "Mastodon.py>=1.2.2",
    ],
    "twilio": [
        "twilio>=6.11.0",
    ],
    "twitter": [
        "python-twitter>=3.4.1",
    ],
    "websocket": [
        "websocket-client>=0.47.0",
    ],
    "xmpp": [
        "xmpppy>=0.6.1",
        "dnspython>=1.16.0",
    ],
    "slixmpp": [
        "slixmpp>=1.5.2",
    ],
    # More notification plugins from the community.
    # https://github.com/daq-tools/mqttwarn-contrib
    "contrib": [
        "mqttwarn-contrib",
    ],
}


# Convenience extra to install *all* dependencies for building a `mqttwarn-full` distribution.
extras_all = []
for extra, packages in extras.items():

    # FIXME: Skip specific packages having build issues.
    # https://github.com/commx/python-rrdtool/issues/36
    if extra in ["mysql", "rrdtool"]:
        continue

    # FIXME: `mysqlclient` needs MySQL or MariaDB client libraries.
    if extra in ["mysql_dynamic"] and sys.platform in ["darwin", "win32"]:
        continue

    # FIXME: Skip specific packages on specific platforms,
    #        because they would also need a build toolchain.
    machine = platform.uname()[4]
    if machine in ["armv7l", "aarch64"] and extra in ["postgres", "slixmpp", "ssh"]:
        continue

    # FIXME: A few packages are not available as wheels on arm32v7, and take quite an amount
    #        of time to build, so let's mask them to improve build times significantly.
    #        Examples: `cryptography`, `aiohttp`, `frozenlist`, `multidict`, `yarl`.
    if machine in ["armv7l"] and extra in ["apprise", "twilio"]:
        continue

    # FIXME: aiohttp (needed by twilio) is not available for Python 3.12 yet.
    if sys.version_info >= (3, 12) and extra in ["twilio"]:
        continue

    for package in packages:
        extras_all.append(package)

extras["all"] = extras_all


# Packages needed for running the tests.
extras["test"] = [
    "pytest<8",
    "pytest-cov<5",
    "pytest-mock<4",
    "pytest-mqtt<1",
    "tox<4",
    "dataclasses; python_version<'3.7'",
    "requests-toolbelt>=1,<2",
    "responses>=0.13.3,<1",
    "pyfakefs>=4.5,<6",
] + extras["all"]

# Packages needed for development and running CI.
extras["develop"] = [
    "black<23",
    "build<1",
    "mypy<1.3",
    "poethepoet<1",
    "ruff==0.0.254; python_version>='3.7'",
    "sphinx-autobuild",
]


setup(
    cmdclass=get_cmdclasses(),
    name="mqttwarn",
    description="mqttwarn - subscribe to MQTT topics and notify pluggable services",
    long_description=README,
    license="EPL 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications",
        "Topic :: Education",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: XMPP",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Archiving",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    author="Jan-Piet Mens, Ben Jones, Andreas Motl",
    author_email="jpmens@gmail.com",
    url="https://github.com/mqtt-tools/mqttwarn",
    keywords="mqtt notification plugins data acquisition push transformation engine mosquitto",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "mqttwarn": [
            "*.ini",
        ],
    },
    zip_safe=False,
    test_suite="tests",
    install_requires=requires,
    extras_require=extras,
    tests_require=extras["test"],
    entry_points={
        "console_scripts": [
            "mqttwarn = mqttwarn.commands:run",
        ],
    },
)
