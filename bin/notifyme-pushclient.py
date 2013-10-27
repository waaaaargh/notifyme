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
from os.path import abspath, dirname, join
sys.path.append(abspath(join(dirname(__file__), '..')))
import logging

from notifyme.pushclient import SSLPushClient
from notifyme.notification import Notification

from argparse import ArgumentParser

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
    parser.add_argument('-r', '--resource', help="push to resource",
                        required=True)
    parser.add_argument('-s', '--subject', help="subject of ntoification",
                        required=True)
    parser.add_argument('-u', '--urgency', help="urgency of ntoification",
                        required=False)
    parser.add_argument('--serverhash', 
                        help="sha256 hash of the server's cert",
                        required=False)

    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)

    client = SSLPushClient(hostname=args.hostname,
                           port=int(args.portnumber),
                           keyfile=args.key,
                           certfile=args.certificate,
                           serverhash=args.serverhash)

    if args.urgency == None:
        urgency = 50

    notification = Notification(subject=args.subject,
                                urgency=urgency,
                                resource=args.resource,
                                data=None)

    client.send_notification(notification)
