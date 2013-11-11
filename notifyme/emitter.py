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

from socket import socket, AF_INET, SOCK_STREAM
from hashlib import sha256
import logging

from OpenSSL import SSL, crypto

from notifyme.messages import NotificationMessage, WrappedProtocolMessage


class SimpleEmitter:
    def __init__(self, connection):
        self.connection = connection

    def send_notification(self, notification):
        message = NotificationMessage(notification)
        wrapped_message = WrappedProtocolMessage(message)
        logging.debug("Sending NotificationMessage")
        self.connection.sendall(wrapped_message.text.encode('utf-8'))


class SSLEmitter:
    def __init__(self, hostname, port, keyfile, certfile, serverhash=None):
        """
        Initialize a SSL Connection to a remote server

        Args:
            hostname: Name or IP address of the host
            port: portnumber on which the host listens
            keyfile: path to the file with the SSL key
            certfile: path to the file with the SSL cert
            serverhash: hex digest of the server's SSL cert as String.
        """
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

        # initialize verification helper
        self._verification_helper = VerificationHelper(server_hash=serverhash)
        self.host = hostname
        self.port = port

        # initialize SSL context
        self._ssl_context = SSL.Context(SSL.TLSv1_METHOD)
        self._ssl_context.use_privatekey_file(keyfile)
        self._ssl_context.use_certificate_file(certfile)
        self._ssl_context.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_CLIENT_ONCE,
                                     self._verification_helper)

    def send_notification(self, notification):
        """
        Send a notification.
        """
        self._conn = SSL.Connection(self._ssl_context,
                                    socket(AF_INET, SOCK_STREAM))
        self._conn.connect((self.host, self.port))
        logging.debug("trying SSL handshake")
        self._conn.do_handshake()

        client = SimpleEmitter(self._conn)
        client.send_notification(notification)

    def shutdown(self):
        self._conn.shutdown()
