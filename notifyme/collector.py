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
import logging
from threading import Thread, Lock
from socket import socket, AF_INET, SOCK_STREAM

from OpenSSL import SSL, crypto

from notifyme.statemachine import ReceivingProtocolState, \
    ProtocolStateMachine
from notifyme.messages import NotificationMessage, ErrorMessage, \
    WrappedProtocolMessage


class CollectorProtocol:
    """
    Protocol spoken by the collector
    """
    def __init__(self, allowed_resources, notification_callback):
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
        if not callable(notification_callback):
            raise ValueError("notification_callback has to be callable!")

        self.allowed_resources = allowed_resources
        self.notification_callback = notification_callback

        self._state = CollectorProtocol.ReceiveNotificationState(self)

    def __call__(self, in_msg):
        self._state, out_msg = self._state(in_msg)
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
                return self,\
                    ErrorMessage("Not allowed to post in this resource")

            try:
                self.context.notification_callback(in_msg.notification)
            except ValueError as e:
                return (self, ErrorMessage(e.message))

            return (self, None)


class SimpleCollector(Thread):
    """
    Simple Collector, interacts with a :class:`socket.connection`
    """
    def __init__(self, connection, notification_callback, allowed_resources):
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
        self.allowed_resources = allowed_resources
        self._protocol = ProtocolStateMachine(
            initial_state=CollectorProtocol.ReceiveNotificationState(self)
        )

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
                out_msg = self._protocol(in_msg)
                self.running = False
            except Exception as e:
                out_msg = ErrorMessage(e.args[0])
            if out_msg is not None:
                try:
                    self.send_message(out_msg)
                except Exception as e:
                    self.running = False


class CollectorDispatcher(Thread):
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
                logging.debug("found unknown cert hash")
                return False
            else:
                self.permitted_resources = res[0][1]
                logging.debug("found known cert hash")
                return True

    def __init__(self, address, port, keyfile, certfile, permissions_table,
                 callback):
        """
        Initialize server dispatcher for publishers

        Args:
            address (string): Address to bind to
            port (int): listen on this port
            keyfile (string): path to keyfile
            certfile (string): path to certfile
            permissions_table (list): list of tuples with sha256 hashes of the
                client's certificate and the list of the resorces the client
                may push to.
        """
        Thread.__init__(self)
        self.running = True
        self.permissions = permissions_table
        self._verifier = CollectorDispatcher.VerificationHelper(
            permissions=permissions_table)
        self.active_connections = []
        self.address = address
        self.port = port
        self.callback = callback

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
        logging.debug("starting CollectorDispatcher")

        while self.running:
            try:
                conn, addr = self._server.accept()
                logging.debug("incoming connection from %s" % str(addr))
                self._verifier.in_use.acquire()
                conn.do_handshake()
                allowed_resources = self._verifier.permitted_resources
                self._verifier.reset()
                self._verifier.in_use.release()

                col = SimpleCollector(connection=conn,
                                      allowed_resources=allowed_resources,
                                      notification_callback=self.callback)
                col.start()

            except KeyboardInterrupt:
                self.running = False
            except SSL.Error:
                self._verifier.reset()
                self._verifier.in_use.release()
            except OSError:
                pass
