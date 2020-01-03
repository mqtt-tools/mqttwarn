# -*- coding: utf-8 -*-
# (c) 2014-2019 The mqttwarn developers
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires = [
    'six==1.13.0',
    'paho-mqtt==1.5.0',
    'jinja2==2.10.3',
    'attrs==19.3.0',
    'docopt==0.6.2',
    'requests==2.22.0',
    'future==0.18.2',
    'configparser==4.0.2',
]

extras = {
    'amqp': [
        'puka==0.0.7',
    ],
    'apns': [
        'apns==2.0.1',
    ],
    'asterisk': [
        'pyst2==0.5.0',
    ],
    'celery': [
        'celery',
    ],
    'dnsupdate': [
        'dnspython==1.15.0',
    ],
    'fbchat': [
        'fbchat==1.3.6',
    ],
    'gss': [
        'gdata==2.0.18',
    ],
    'gss2': [
        'gspread==2.1.1',
        'oauth2client==4.1.2',
        #'google-api-python-client==1.7.11',
    ],
    'iothub': [
        'iothub-client==1.1.2.0',
    ],
    'mysql': [
        'mysql',
    ],
    'nma': [
        'PyNMA==1.0',
    ],
    'nsca': [
        'pynsca==1.6',
    ],
    'osxnotify': [
        'pync==1.6.1',
    ],
    'pastebinpub': [
        'Pastebin==1.1.2',
    ],
    'postgres': [
        'psycopg2==2.7.4',
    ],
    'prowl': [
        'prowlpy>=0.52',
    ],
    'pushbullet': [
        'PushbulletPythonLibrary==2.3',
    ],
    'redispub': [
        'redis==2.10.6',
    ],
    'rrdtool': [
        'rrdtool==0.1.12',
    ],
    'serial': [
        'pyserial==3.4',
    ],
    'slack': [
        'slacker==0.9.65',
    ],
    'ssh': [
        'paramiko==2.4.1',
    ],
    'tootpaste': [
        'Mastodon.py==1.2.2',
    ],
    'twilio': [
        'twilio==6.11.0',
    ],
    'twitter': [
        'python-twitter==3.4.1',
    ],
    'websocket': [
        'websocket-client==0.47.0',
    ],
    'xively': [
        'xively-python',
    ],
    'xmpp': [
        'xmpppy==0.5.0rc1',
    ],
    'test': [
        'pytest==4.6.7',
        'pytest-cov==2.8.1',
        'lovely.testlayers>=0.7.1',
        'tox==3.14.2',
    ],
}

setup(name='mqttwarn',
      version='0.13.5',
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
        "Programming Language :: Python :: 2.7",
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
      dependency_links=[
          'https://github.com/jacobb/prowlpy/archive/master.tar.gz#egg=prowlpy'
      ],
      entry_points={
          'console_scripts': [
              'mqttwarn = mqttwarn.commands:run',
          ],
      },
)
