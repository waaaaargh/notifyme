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

from notifyme.messages import NotificationMessage, WrappedProtocolMessage

class SimplePushClient:
    def __init__(self, connection):
        self.connection = connection

    def send_notification(self, notification):
        message = NotificationMessage(notification.to_dict)
        wrapped_message = WrappedProtocolMessage(message)
        self.connection.sendall(wrapped_message.text.encode('utf-8'))
