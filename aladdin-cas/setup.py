#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup

setup(
    name="pandora",
    version="1.0.1",
    install_requires=[
        "tornado",
        "requests",
        "configparser",
        "xpinyin",
        "jieba",
        "numpy",
        "scipy",
        "protobuf",
    ],
    description="Zabbix API Python interface",
    author="Luke Cyca",
    author_email="me@lukecyca.com",
    license="LGPL",
    keywords="zabbix monitoring api",
    url="http://github.com/lukecyca/pyzabbix",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    packages=['src'],
    tests_require=[
        "nose2",
    ],
    test_suite='nose2.collector.collector',
)

