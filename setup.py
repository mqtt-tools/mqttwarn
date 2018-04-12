# -*- coding: utf-8 -*-
# (c) 2014-2018 The mqttwarn developers
import sys
from setuptools import setup, find_packages

requires = [
    'paho-mqtt==1.2',               # 1.3.1
    'jinja2==2.8',
    'attrs==17.4.0',
    'requests==2.18.4',
]

extras = {
    'xmpp': [
        'xmpppy==0.5.0rc1',
    ],
}

setup(name='mqttwarn',
      version='0.7.0',
      description='mqttwarn - subscribe to MQTT topics and notify pluggable services',
      long_description='mqttwarn subscribes to any number of MQTT topics and publishes received payloads to one or more '
                       'notification services after optionally applying sophisticated transformations.',
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
        # The EPL 2.0 license isn't approved by the OSI yet,
        # at least its not available at https://pypi.python.org/pypi?%3Aaction=list_classifiers.
        # In the meanwhile, we will use EPL 1.0 here.
        "License :: OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Education",
        "Topic :: Internet",
        "Topic :: Internet :: MQTT",
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
      author='Jan-Piet Mens, Ben Jones',
      author_email='jpmens()gmail.com, ben.jones12()gmail.com',
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
      test_suite='mqttwarn.test',
      install_requires=requires,
      extras_require=extras,
      dependency_links=[
      ],
      entry_points={
          'console_scripts': [
              'mqttwarn = mqttwarn.commands:run',
          ],
      },
)
