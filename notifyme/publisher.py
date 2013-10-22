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
from threading import Thread, Lock
from socket import socket, AF_INET, SOCK_STREAM
from hashlib import sha256

from OpenSSL import SSL, crypto

from notifyme.statemachine import SendingProtocolState, \
    ReceivingProtocolState, ProtocolStateMachine
from notifyme.messages import PublishMessage, SubscribeMessage, \
    ConfirmationMessage, ErrorMessage, WrappedProtocolMessage, \
    NotificationMessage


class PublisherProtocol:
    """
    Protocol as speaken by a publisher
    """
    def __init__(self, published_resources):
        """
        Initializes a PublisherProtocol

        Args:
            published_resources(list): List of resources this publisher
                is going to publish.
        """
        self.published_resources = published_resources
        self.subscribed_resources = []
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
        """
        State that sends a PublishMessage
        """
        def __call__(self):
            logging.debug("Sending PublishMessage")
            return PublisherProtocol.ReceiveSubscriptionMessageState(
                self.context), \
                PublishMessage(published_resources=
                               self.context.published_resources)

    class ReceiveSubscriptionMessageState(ReceivingProtocolState):
        """
        State that expects SubscribeMessages.
        """
        def __call__(self, in_msg):
            """
            Handle incoming SubscribedMessage

            Args:
                in_msg (:class:`notifyme.messages.SubscribeMessage`): Message
                    to handle
            """
            if type(in_msg) is not SubscribeMessage:
                return ErrorMessage("Unexpected Message")
            logging.debug("Received SubscribeMessage")
            confirmed_resources = []
            unavailable_resources = []
            # check if subscribed resources are valid.
            for resource in in_msg.data['subscribed_resources']:
                if resource in self.context.published_resources:
                    confirmed_resources += [resource]
                else:
                    unavailable_resources += [resource]

            if len(unavailable_resources) > 0:
                logging.debug("The Client requested some unavailable \
                        resources")
                out_msg = ErrorMessage(error_message=
                                       "Some resources were unavailable")
            else:
                out_msg = ConfirmationMessage(confirmed_resources=
                                              confirmed_resources)
                self.context.subscribed_resources = confirmed_resources

            return (self, out_msg)


class SimplePublisher(Thread):
    """
    Handles a connection from a subscriber
    """
    def __init__(self, connection, published_resources, dispatcher):
        """
        Initialize connection and protocol

        Args:
            connection (:class:`socket.connection`):
                Connection throug which to send and receive data
            published_resources (list):
                List of resources the client may subscribe to.
            dispatcher (:class:`notifyme.publisher.PublisherDispatcher`):
                dispatcher that spawned this publisher.
        """
        Thread.__init__(self)
        self.running = True
        self.lock = Lock()
        self.connection = connection
        self.published_resources = published_resources
        self.subscribed_resources = []
        self.dispatcher = dispatcher
        self._protocol = ProtocolStateMachine(initial_state=PublisherProtocol
                                              .SendPublishMessageState(self))

    def send_message(self, message):
        """
        Send a message to the connected peer

        Args:
            message(:class:`notifyme.messages.ProtocolMessage`):
                message to be sent.
        """
        wrapped_message = WrappedProtocolMessage(message)
        self.lock.acquire()
        self.connection.send(wrapped_message.text.encode('utf-8'))
        self.lock.release()

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
                out_msg = self._protocol(in_msg)
            except Exception as e:
                out_msg = ErrorMessage(e.args[0])
            if out_msg is not None:
                try:
                    self.send_message(out_msg)
                except Exception as e:
                    self.running = False
        self.dispatcher.active_connections.remove(self)

    def send_notification(self, notification):
        """
        Send out a notification message to the peer.
        """
        notification_message = NotificationMessage(notification)
        self.send_message(message=notification_message)


class PublisherDispatcher(Thread):
    """
    Server Thread that spawns a new `SimplePublisher` everytime a
    Client with a valid client certificate connects.
    """

    class VerificationHelper:
        """
        Helper that serves as verify_callback for OpenSSL
        """
        def __init__(self, permissions):
            """
            Initialize Helper and set permissions. Saves the permitted
            resources of the incoming certificate in `permitted_resources`.
            call `reset()` before you re-use it!

            Args:
                permissions: list of tuples, each consisting of the
                    hex representation of a sha256 hash as a string
                    and a list of allowed resources, each as a string.
            """
            self.permissions = permissions
            self.permitted_resources = []
            self.in_use = Lock()


        def reset(self):
            """
            Resets the object, call before reuse!
            """
            self.permitted_resources = []

        def __call__(self, conn, cert, a, b, c):
            """
            Actually perform the verification
            """
            # determine certificate sha256 hash
            cert_hash = sha256()
            cert_hash.update(crypto.dump_certificate(1, cert))
            cert_hashdigest = cert_hash.hexdigest()

            # check against permissions table
            res = list(filter(lambda x: x[0] == cert_hashdigest,
                              self.permissions))
            if len(res) < 1:
                return False
                logging.debug("found unknown cert hash")
            else:
                self.permitted_resources = res[0][1]
                logging.debug("found known cert hash")
                return True

    def __init__(self, address, port, keyfile, certfile, permissions_table):
        """
        Initialize server dispatcher for publishers

        Args:
            address (string): Address to bind to
            port (int): listen on this port
            keyfile (string): path to keyfile
            certfile (string): path to certfile
            permissions_table (list): list of tuples with sha256 hashes of the
                client's certificate and the list of the resorces the client
                may subscribe to.
        """
        Thread.__init__(self)
        self.running = True
        self.permissions = permissions_table
        self._verifier = PublisherDispatcher.VerificationHelper(
            permissions=permissions_table)
        self.active_connections = []
        self.address = address
        self.port = port

        # initialize SSL Context
        self._ssl_context = SSL.Context(SSL.TLSv1_METHOD)
        self._ssl_context.use_privatekey_file(keyfile)
        self._ssl_context.use_certificate_file(certfile)
        self._ssl_context.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_CLIENT_ONCE,
                                     self._verifier)

    def run(self):
        self._server = SSL.Connection(self._ssl_context,
                                      socket(AF_INET, SOCK_STREAM))
        self._server.bind((self.address, self.port))
        self._server.listen(5)
        logging.debug("starting publisherDispatcher")

        while self.running:
            try:
                conn, addr = self._server.accept()
                logging.debug("incoming connection from %s" % str(addr))
                self._verifier.in_use.acquire()
                conn.do_handshake()
                permitted_resources = self._verifier.permitted_resources
                self._verifier.reset()
                self._verifier.in_use.release()
                # start Publisher Thread
                pub = SimplePublisher(connection=conn,
                                      published_resources=permitted_resources,
                                      dispatcher=self)
                self.active_connections.append(pub)
                pub.start()
            except (SystemExit, KeyboardInterrupt):
                import pdb; pdb.set_trace()
                logging.debug("Shutting down, thanks for flying notifyme!")
                self.running = False
            except SSL.Error:
                self._verifier.reset()
                self._verifier.in_use.release()
            except OSError:
                pass

    def send_notification(self, notification):
        """
        Send notifications to connected nodes that have subscribed to matching
        resources

        Args:
            notification(:class:`notifyme.notification.Notification`):
                Notification to send.
        """

        for p in self.active_connections:
            if notification.resource in p.subscribed_resources:
                logging.debug("sending message...")
                p.send_notification(notification)
