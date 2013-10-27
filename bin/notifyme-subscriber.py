#!/usr/bin/env python3
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

import sys
from os.path import abspath, dirname, join, exists
sys.path.append(abspath(join(dirname(__file__), '..')))
import logging

from time import sleep
from notifyme.subscriber import SimpleSubscriber

from argparse import ArgumentParser


def notification_callback(notification):
    """
    This function is called whenever a notification comes in.

    Args:
        notification(:class:`notifyme.notification.Notification`):
            Notification that has been received from the publisher.
    """
    print("NOTIFICATION: %s" % notification['subject']) 


if __name__ == '__main__':
    parser = ArgumentParser(description="Notifyme subscriber component")
    parser.add_argument('-k', '--key', help="key file",
                        required=True)
    parser.add_argument('-c', '--certificate', help="certificate file",
                        required=True)
    parser.add_argument('-n', '--hostname', help="publisher hostname",
                        required=True)
    parser.add_argument('-p', '--portnumber', help="publisher port",
                        required=True)
    parser.add_argument('-r', '--resource', help="subscribe to resource",
                        required=True, action='append')
    args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    subscriber = SimpleSubscriber(hostname=args.hostname,
                                  port=int(args.portnumber),
                                  certfile=args.certificate,
                                  keyfile=args.key,
                                  notification_callback=notification_callback,
                                  subscribed_resources=args.resource)
    subscriber.daemon = True
    try:
        subscriber.run()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        sys.exit(1)
    try:
        while subscriber.running:
            sleep(1)
    except KeyboardInterrupt:
        logging.debug("Caught KeyboardInterrupt, exitting...")
        subscriber.running = False
