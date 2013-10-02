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
from threading import Thread

from notifyme.statemachine import ReceivingProtocolState, \
    SendingProtocolState, ProtocolStateMachine
from notifyme.messages import NotificationMessage, ErrorMessage, \
    WrappedProtocolMessage


class CollectorProtocol:
    """
    Protocol spoken by the collector
    """
    def __init__(self, notification_callback, allowed_resources):
        """
        Initialize a new CollectorProtocol

        Args:
            notification_callback(:class:`types.FunctionType`):
                Execute this function, whenever we receive a notification.
                Gets the received NotificationMessage as first argument.
                should throw a `ValueError` if anything is wrong. The
                `message` property will be handed back to the sender
                inside of a :class:`notifyme.messages.ErrorMessage`.

            allowed_resources(list): List of resources the connected client
                is allowed to push to.

        """
        if type(notification_callback) is not FunctionType:
            raise ValueError("notification_callback has to be callable!")

        self.notification_callback = notification_callback
        self.allowed_resources = allowed_resources
        self._state = CollectorProtocol.ReceiveNotificationState(self)

    def __call__(self, in_msg):
        self._state, out_msg = self._state(in_msg)
        if out_msg is not None:
            return out_msg

    class ReceiveNotificationState(ReceivingProtocolState):
        """
        Initial State of a collector Thread
        """
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

            if in_msg.data['resource'] not in self.context.allowed_resources:
                return self, ErrorMessage("Not allowed to post in this resource")

            try:
                self.context.notification_callback(in_msg)
            except ValueError as e:
                return (self, ErrorMessage(e.message))

            return (self, None)


class SimpleCollector(Thread):
    """
    Simple Collector, interacts with a :class:`socket.connection`
    """
    def __init__(self, connection, notification_callback):
        """
        Create a new SimpleCollector that handles a `socket.connection`

        Args:
            connection(:class:`socket.connection`): Network connection
                to the peer

            notification_callback(:class:`types.FunctionType`): callable
                object that is being called when a notification is
                received

        """
        Thread.__init__(self)
        self.connection = connection
        self.running = True
        self.notification_callback = notification_callback
        self._protocol = ProtocolStateMachine(
            initial_state=CollectorProtocol(self))

    def send_message(self, message):
        """
        Send a message to the connected peer

        Args:
            message(:class:`notifyme.messages.ProtocolMessage`):
                message to be sent.
        """
        wrapped_message = WrappedProtocolMessage(message)
        self.connection.send(wrapped_message.text.encode('utf-8'))

    def receive_message(self):
        """
        Receives a message from the connected Peer, blocks as long
        as it doesn't receive any.

        Returns:
            :class:`notifyme.messages.ProtocolMessage`
        """
        received_bytes = self.connection.recv(1024)
        received_string = received_bytes.decode('utf-8')
        in_msg = WrappedProtocolMessage.parse(received_string)
        return in_msg

    def run(self):
        """
        Handle the communication with a peer.
        """
        while self.running:
            try:
                if self._protocol.wait_for_input:
                    in_msg = self.receive_message()
                else:
                    in_msg = None
                out_msg = self.protocol(in_msg)
            except Exception as e:
                out_msg = ErrorMessage(e.args[0])
            if out_msg is not None:
                try:
                    self.send_message(out_msg)
                except Exception as e:
                    self.running = False
