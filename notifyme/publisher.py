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

from notifyme.statemachine import SendingProtocolState, ReceivingProtocolState
from notifyme.messages import PublishMessage, SubscribeMessage, \
    ConfirmationMessage, ErrorMessage


class PublisherProtocol:
    def __init__(self, published_resources):
        """
        Initializes a PublisherProtocol

        Args:
            published_resources(list): List of resources this publisher
                is going to publish.
        """
        self.published_resources = published_resources
        self._state = PublisherProtocol.SendPublishMessageState(self)

    def __call__(self, in_msg):
        """
        React appropriately to an incoming message.

        Returns:
            :class:`notifyme.messages.ProtocolMessage` or None
        """
        if isinstance(self._state, ReceivingProtocolState):
            self._state, out_msg = self._state(in_msg)
        else:
            self._state, out_msg = self._state()
        return out_msg

    class SendPublishMessageState(SendingProtocolState):
        def __call__(self):
            return PublisherProtocol.ReceiveSubscriptionMessageState(
                self.context), \
                PublishMessage(published_resources=
                               self.context.published_resources)

    class ReceiveSubscriptionMessageState(ReceivingProtocolState):
        def __call__(self, in_msg):
            """
            Handle incoming SubscribedMessage

            Args:
                in_msg (:class:`notifyme.messages.SubscribeMessage`): Message
                    to handle
            """
            if type(in_msg) is not SubscribeMessage:
                return ErrorMessage("Unexpected Message")
            confirmed_resources = []
            unavailable_resources = []
            # check if subscribed resources are valid.
            for resource in in_msg.data['subscribed_resources']:
                if resource in self.context.published_resources:
                    confirmed_resources += [resource]
                else:
                    unavailable_resources += [resource]

            if len(unavailable_resources) > 0:
                out_msg = ErrorMessage(error_message=
                                       "Some resources were unavailable")
            else:
                out_msg = ConfirmationMessage(confirmed_resources=
                                              confirmed_resources)

            return (self, out_msg)
