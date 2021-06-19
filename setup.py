# -*- coding: utf-8 -*-
# (c) 2014-2021 The mqttwarn developers
import os
import platform

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires = [
    'six>=1.13.0',
    'paho-mqtt>=1.4.0',
    'jinja2>=2.10.1',
    'attrs>=19.3.0',
    'docopt>=0.6.2',
    'requests>=2.22.0',
    'future>=0.18.2',
    'configparser>=3.5.3',
]

extras = {
    'amqp': [
        'puka>=0.0.7',
    ],
    'apns': [
        'apns>=2.0.1',
    ],
    'apprise': [
        'apprise>=0.8.9',
    ],
    'asterisk': [
        'pyst2>=0.5.0',
    ],
    'celery': [
        'celery',
    ],
    'chromecast': [
        'pychromecast>=7.5.0',
    ],
    'dnsupdate': [
        'dnspython>=1.15.0',
    ],
    'fbchat': [
        'fbchat>=1.3.6',
    ],
    'gss': [
        'gdata>=2.0.18',
    ],
    'gss2': [
        'gspread>=2.1.1',
        'oauth2client>=4.1.2',
        #'google-api-python-client>=1.7.11',
    ],
    'mysql': [
        'mysql',
    ],
    'nma': [
        'PyNMA>=1.0',
    ],
    'nsca': [
        'pynsca>=1.6',
    ],
    'osxnotify': [
        'pync>=1.6.1',
    ],
    'pastebinpub': [
        'Pastebin>=1.1.2',
    ],
    'postgres': [
        'psycopg2-binary>=2.7.4',
    ],
    'prowl': [
        'pyprowl>=3.0.1',
    ],
    'pushbullet': [
        'PushbulletPythonLibrary>=2.3',
    ],
    'redispub': [
        'redis>=2.10.6',
    ],
    'rrdtool': [
        'rrdtool>=0.1.12',
    ],
    'serial': [
        'pyserial>=3.4',
    ],
    'slack': [
        'slack-sdk>=3.1.0',
    ],
    'ssh': [
        'paramiko>=2.4.1',
    ],
    'tootpaste': [
        'Mastodon.py>=1.2.2',
    ],
    'twilio': [
        'twilio>=6.11.0',
    ],
    'twitter': [
        'python-twitter>=3.4.1',
    ],
    'websocket': [
        'websocket-client>=0.47.0',
    ],
    'xively': [
        'xively-python',
    ],
    'xmpp': [
        'xmpppy>=0.6.1',
        'dnspython>=1.16.0',
    ],
    'slixmpp': [
        'slixmpp>=1.5.2',
    ],
    # More notification plugins from the community.
    # https://github.com/daq-tools/mqttwarn-contrib
    'contrib': [
        'mqttwarn-contrib',
    ],
}


# Convenience extra to install *all* dependencies for building a `mqttwarn-full` distribution.
extras_all = []
for extra, packages in extras.items():

    # FIXME: Skip specific packages having build issues.
    # https://github.com/commx/python-rrdtool/issues/36
    if extra in ["mysql", "rrdtool"]:
        continue

    # FIXME: Skip specific packages on specific platforms,
    #        because they would also need a build toolchain.
    machine = platform.uname()[4]
    if machine in ["armv7l", "aarch64"] and extra in ["postgres", "slixmpp", "ssh"]:
        continue

    # FIXME: The `cryptography` package is not available as binary wheel on arm32v7.
    if machine in ["armv7l"] and extra in ["apprise"]:
        continue

    for package in packages:
        extras_all.append(package)

extras["all"] = extras_all


# Packages needed for running the tests.
extras["test"] = [
    'pytest>=4.6.7',
    'pytest-cov>=2.8.1',
    'lovely.testlayers>=0.7.1',
    'tox>=3.14.2',
    'surrogate==0.1',
    'dataclasses; python_version<"3.7"',
    'requests-toolbelt>=0.9.1,<1',
    'responses>=0.13.3,<1',
]


setup(name='mqttwarn',
      version='0.26.1',
      description='mqttwarn - subscribe to MQTT topics and notify pluggable services',
      long_description=README,
      license="EPL 2.0",
      classifiers=[
        "Development Status :: 4 - Beta",
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
      author='Jan-Piet Mens, Ben Jones, Andreas Motl',
      author_email='jpmens@gmail.com',
      url='https://github.com/jpmens/mqttwarn',
      keywords='mqtt notification plugins data acquisition push transformation engine ' +
               'mosquitto ',
      packages=find_packages(),
      include_package_data=True,
      package_data={
        'mqttwarn': [
          '*.ini',
        ],
      },
      zip_safe=False,
      test_suite='tests',
      install_requires=requires,
      extras_require=extras,
      tests_require=extras['test'],
      entry_points={
          'console_scripts': [
              'mqttwarn = mqttwarn.commands:run',
          ],
      },
)
