#!/usr/bin/env python3
# encoding: utf-8
# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes
# This file is part of notifyme.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

import sys
from os.path import abspath, dirname, join, exists
from socket import SHUT_RDWR
sys.path.append(abspath(join(dirname(__file__), '..')))
import argparse

try:
    import yaml
except ImportError as e:
    print("[!] pyYaml is required for notifymed!")
    sys.exit(1)
try:
    from OpenSSL import SSL
except ImportError as e:
    print("[!] pyOpenSSL is required for notifymed!")
    sys.exit(1)


from time import sleep
from threading import Thread

from notifyme.notification import Notification
from notifyme.publisher import PublisherDispatcher
from notifyme.collector import CollectorDispatcher


def load_config_from_file(file):
    with open(file) as f:
        return yaml.safe_load(f)


class TestNotificationManager(Thread):
    def __init__(self, publisher_dispatcher):
        """
        Args:
            publisher_dispatcher:
                Dispatcher that knows the publisher threads
        """
        Thread.__init__(self)
        self.dispatcher = publisher_dispatcher

    def __call__(self, notification):
        self.dispatcher.send_notification(notification)

    def run(self):
        n = Notification(data=None, resource='/foo', urgency=88,
                         subject='Test notification')
        while True:
            logging.debug("sending message...")
            self(n)
            sleep(5)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=
                                "NotifyMe collector and publisher daemon")
    p.add_argument('--config-file', '-f', help="Set location for config file")
    p.add_argument('--check-config', '-c', help="Check config file")

    args = p.parse_args()

    if args.config_file is not None:
        config = load_config_from_file(file=args.config_file)
    elif exists('/etc/notifyme/config.yml'):
        config = load_config_from_file('/etc/notifyme/config.yml')
    elif exists('notifyme.yml'):
        config = load_config_from_file('notifyme.yml')
    else:
        print("[!] config file not found!")
        sys.exit(1)

    # build permission tables
    publisher_permissions = [(o['hash'], o['resources']) for o in
                             config['publisher']['permissions']]
    collector_permissions = [(o['hash'], o['resources']) for o in
                             config['collector']['permissions']]

    # start publisher dispatcher
    pub = PublisherDispatcher(address='localhost',
                              port=config['publisher']['port'],
                              keyfile=config['publisher']['keyfile'],
                              certfile=config['publisher']['certfile'],
                              permissions_table=publisher_permissions)

    def test_cb(n):
        print("lel")


    # start collector dispatcher
    col = CollectorDispatcher(address='localhost',
                              port=config['collector']['port'],
                              keyfile=config['collector']['keyfile'],
                              certfile=config['collector']['certfile'],
                              permissions_table=collector_permissions,
                              callback=test_cb)

    class SigintHandler:
        def __init__(self, col_dispatcher, pub_dispatcher):
            self.col_dispatcher = col_dispatcher
            self.pub_dispatcher = pub_dispatcher

        def __call__(self, signum, frame):
            self.col_dispatcher.running = False
            self.col_dispatcher._server.sock_shutdown(SHUT_RDWR)
            self.pub_dispatcher.running = False
            self.pub_dispatcher._server.sock_shutdown(SHUT_RDWR)

    import signal
    signal.signal(signal.SIGINT, SigintHandler(pub, col))

    pub.start()
    col.start()
