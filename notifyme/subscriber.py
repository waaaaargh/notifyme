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

from notifyme.messages import SubscribeMessage, ConfirmationMessage, \
        PublishMessage, ErrorMessage, NotificationMessage
from notifyme.statemachine import ReceivingProtocolState, SendingProtocolState
from notifyme.statemachine import ProtocolStateMachine


class SubscriberProtocol(ProtocolStateMachine):
    def __init__(self, notification_callback, subscribed_resources):
        self.context = {
            'subscribed_resources': subscribed_resources,
            'notification_callback': notification_callback
        }
        init_state = SubscriberProtocol.ReceivePublishMessageState(
            self.context)
        ProtocolStateMachine.__init__(self, init_state)

    class ReceivePublishMessageState(ReceivingProtocolState):
        def __call__(self, in_msg):
            self.context['published_resources'] = \
                in_msg.data['published_resources']
            sub_msg = SubscribeMessage(subscribed_resources=\
                self.context['subscribed_resources'])
            return SubscriberProtocol.ReceiveConfirmMessageState(
                self.context), sub_msg

    class ReceiveConfirmMessageState(ReceivingProtocolState):
        def __call__(self, in_msg):
            if not isinstance(in_msg, ConfirmationMessage):
                return (None, None)
            return SubscriberProtocol.ReceiveNotificationState(
                self.context), None

    class ReceiveNotificationState(ReceivingProtocolState):
        def __call__(self, in_msg):
            if not isinstance(in_msg, NotificationMessage):
                return self, ErrorMessage(error_message=\
                    "Unexpected ProtocolMessage")
            self.context['notification_callback'](in_msg.data)

            return self, None
