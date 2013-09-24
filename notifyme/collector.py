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

from types import FunctionType
from notifyme.messages import NotificationMessage, ErrorMessage


class CollectorProtocol:
    """
    Protocol spoken by the collector
    """
    def __init__(self, notification_callback):
        """
        Initialize a new CollectorProtocol

        Args:
            notification_callback(:class:`types.FunctionType`):
                Execute this function, whenever we receive a notification.
                Gets the received NotificationMessage as first argument.
                should throw a `ValueError` if anything is wrong. The
                `message` property will be handed back to the sender
                inside of a :class:`notifyme.messages.ErrorMessage`.

        """
        if type(notification_callback) is not FunctionType:
            raise ValueError("notification_callback has to be callable!")

        self._state = CollectorProtocol.ReceiveState(notification_callback)

    def __call__(self, in_msg):
        self._state, out_msg = self._state(in_msg)
        if out_msg is not None:
            return out_msg

    class ReceiveState:
        """
        Initial State of a collector Thread
        """
        def __init__(self, notification_callback):
            """
            Initialize a new State object.

            """
            self.notification_callback = notification_callback

        def __call__(self, in_msg):
            """
            Properly handle incoming ProtocolMessages.

            Args:
                in_msg(:class:`notifyme.messages.ProtocolMessage`):
                    Message to handle

            Returns:
                Tuple of new state and optional ErrorMessage
            """
            if type(in_msg) is not NotificationMessage:
                return (self, ErrorMessage("This node only accepts \
                                           NotificationMessages"))
            try:
                self.notification_callback(in_msg)
            except ValueError as e:
                return (self, ErrorMessage(e.message))

            return (self, None)
