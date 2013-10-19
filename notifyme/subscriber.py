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

from hashlib import sha256
from OpenSSL import SSL, crypto
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
import logging

from notifyme.messages import SubscribeMessage, ConfirmationMessage, \
    ErrorMessage, NotificationMessage, PublishMessage, WrappedProtocolMessage
from notifyme.statemachine import ReceivingProtocolState
from notifyme.statemachine import ProtocolStateMachine


class SubscriberProtocol(ProtocolStateMachine):
    """
    Represents the state machine that handles all the interaction
    with a Publisher from a Subscriber's point of view
    """
    def __init__(self, notification_callback, subscribed_resources):
        """
        Initialize a Subscriber

        Args:
            notification_callback(:class:`types.FunctionType`): callable that
                is called everytime the subscriber receives a Notification
                Message. Gets the notification_message as its first positional
                argument.
            subscribed_resources(list): list of resource identifiers
                (str)
        """
        self.context = {
            'subscribed_resources': subscribed_resources,
            'notification_callback': notification_callback
        }
        init_state = SubscriberProtocol.ReceivePublishMessageState(
            self.context)
        ProtocolStateMachine.__init__(self, init_state)

    class ReceivePublishMessageState(ReceivingProtocolState):
        """
        Wait for a `notifyme.messages.PublishMessage` and return a
        `notifyme.messages.SubscribeMessage`.
        """
        def __call__(self, in_msg):
            if not isinstance(in_msg, PublishMessage):
                return self, None
            self.context['published_resources'] = \
                in_msg.data['published_resources']
            sub_msg = SubscribeMessage(subscribed_resources=
                                       self.context['subscribed_resources'])
            logging.debug("received PublishMessage")
            return SubscriberProtocol.ReceiveConfirmMessageState(
                self.context), sub_msg

    class ReceiveConfirmMessageState(ReceivingProtocolState):
        """
        Wait for a `notifyme.messages.ConfirmationMessage`
        """
        def __call__(self, in_msg):
            if isinstance(in_msg, ErrorMessage):
                logging.critical('Some resources were not available')
                raise Exception('Some subscribed resources were not available!')
            elif not isinstance(in_msg, ConfirmationMessage):
                return self, None
            logging.debug("received ConfirmationMessage")
            return SubscriberProtocol.ReceiveNotificationState(
                self.context), None

    class ReceiveNotificationState(ReceivingProtocolState):
        """
        Receive and Handle a `notifyme.messages.NotificationMessage`
        """
        def __call__(self, in_msg):
            if not isinstance(in_msg, NotificationMessage):
                return self, ErrorMessage(error_message=
                                          "Unexpected ProtocolMessage")
            logging.debug("received NotificationMessage")
            self.context['notification_callback'](in_msg.data)

            return self, None


class SimpleSubscriber(Thread):
    def __init__(self, hostname, port, certfile, keyfile,
                 subscribed_resources, notification_callback,
                 serverhash=None):
        class VerificationHelper:
            def __init__(self, server_hash):
                self.server_hash = server_hash

            def __call__(self, conn, cert, a, b, c):
                if self.server_hash is not None:
                    cert_hash = sha256()
                    cert_hash.update(crypto.dump_certificate(1, cert))
                    if cert_hash.hexdigest() == self.server_hash:
                        return True
                else:
                    return True

        Thread.__init__(self)
        self.hostname = hostname
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.serverhash = serverhash
        self.verification_helper = VerificationHelper(serverhash)
        self.lock = Lock()

        self._ssl_context = SSL.Context(SSL.TLSv1_METHOD)
        self._ssl_context.use_privatekey_file(keyfile)
        self._ssl_context.use_certificate_file(certfile)
        self._ssl_context.set_verify(SSL.VERIFY_NONE, self.verification_helper)

        self._protocol = SubscriberProtocol(
            notification_callback=notification_callback,
            subscribed_resources=subscribed_resources)

    def send_message(self, message):
        """
        Send a message to the connected peer

        Args:
            message(:class:`notifyme.messages.ProtocolMessage`):
                message to be sent.
        """
        wrapped_message = WrappedProtocolMessage(message)
        self.lock.acquire()
        self._sock.send(wrapped_message.text.encode('utf-8'))
        self.lock.release()

    def receive_message(self):
        """
        Receives a message from the connected Peer, blocks as long
        as it doesn't receive any.

        Returns:
            :class:`notifyme.messages.ProtocolMessage`
        """
        received_bytes = self._sock.recv(1024)
        received_string = received_bytes.decode('utf-8')
        in_msg = WrappedProtocolMessage.parse(received_string)
        return in_msg

    def run(self):
        logging.debug("starting subscriber")
        # set up network connection
        self._sock = SSL.Connection(self._ssl_context,
                                    socket(AF_INET, SOCK_STREAM))
        self._sock.connect((self.hostname, self.port))
        try:
            logging.debug("trying SSL Handshake")
            self._sock.do_handshake()
        except SSL.Error:
            pass
        while True:
            if self._protocol.wait_for_input:
                in_msg = self.receive_message()
            else:
                in_msg = None

            out_msg = self._protocol(in_msg)
            if out_msg is not None:
                self.send_message(out_msg)
