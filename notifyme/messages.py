# -*- coding: utf-8 -*-
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

import json


class ProtocolMessage:
    """
    Base class for all protocol Messages
    """
    def __init__(self):
        """
        Initialize Protocol Message
        """
        self.data = {}

    @property
    def text(self):
        """
        Text representation of this Message, ready to be sent over the wire
        """
        return json.dumps(self.data)

    @property
    def wrapped(self):
        return WrappedProtocolMessage(self)


class PublishMessage(ProtocolMessage):
    """
    Announce published resources to the subscriber
    """
    def __init__(self, published_resources):
        ProtocolMessage.__init__(self)
        self.data['published_resources'] = published_resources


class SubscribeMessage(ProtocolMessage):
    """
    Subscribe to notifications from publisher
    """
    def __init__(self, subscribed_resources):
        ProtocolMessage.__init__(self)
        self.data['subscribed_resources'] = subscribed_resources


class ConfirmationMessage(ProtocolMessage):
    """
    Confirm subscriptions
    """
    def __init__(self, confirmed_resources):
        ProtocolMessage.__init__(self)
        self.data['confirmed_resources'] = confirmed_resources


class ErrorMessage(ProtocolMessage):
    """
    Notify peer if any errors occur
    """
    def __init__(self, error_message):
        self.data['error_message'] = error_message


class NotificationMessage(ProtocolMessage):
    """
    Send notifications
    """
    def __init__(self, notification):
        ProtocolMessage.__init__(self)
        self.data = notification


class WrappedProtocolMessage:
    """
    Message wrapped up for transport
    """
    def __init__(self, message):
        """
        Create a wrapped protocol message from a plain ProtocolMessage

        Args:
            message(:class:`notifyme.messages.ProtocolMessage`): message that
                shall be wrapped for transport
        """
        self.data = {
            'message_type': type(message).__name__,
            'message': message}

        @property
        def text(self):
            """
            Text representation of the message, ready to be sent over the wire
            """
            return json.dumps(self.data)
