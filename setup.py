#!/usr/bin/env python
# encoding: utf-8
# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes

from distutils.core import setup

setup(
    name="notifyme-common",
    packages=["notifyme"],
    version="0.1~dev1",
    description="Notification transport library",
    author="Johannes Fürmann",
    author_email="johannes@fuermann.cc",
    url="https://github.com/waaaaargh/notifyme",
    scripts=["bin/notifyme-gencert"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: System :: Networking"
    ]
    )
