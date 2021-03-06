#!/usr/bin/env python
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


from argparse import ArgumentParser
from socket import gethostname
from OpenSSL import crypto
from hashlib import sha256

def gen_cert(outfile):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    c = crypto.X509()

    c.get_subject().C = "US"
    c.get_subject().ST = "Minnesota"
    c.get_subject().L = "Minnetonka"
    c.get_subject().O = "my company"
    c.get_subject().OU = "my organization"
    c.get_subject().CN = gethostname()
    c.set_serial_number(1000)
    c.gmtime_adj_notBefore(0)
    c.gmtime_adj_notAfter(10*365*24*60*60)
    c.set_issuer(c.get_subject())

    c.set_pubkey(k)
    c.sign(k, 'sha1')

    with open(outfile, 'w') as f:
        f.write(crypto.dump_certificate(1, c).decode('utf-8'))
        f.write(crypto.dump_privatekey(1, k).decode('utf-8'))

    cert_hash = sha256()
    cert_hash.update(crypto.dump_certificate(1, c))
    return cert_hash.hexdigest()


if __name__ == "__main__":
    parser = ArgumentParser(description="Create self-signed certificates for \
                            notifyme.")
    parser.add_argument("-o", "--out", help="Write certificate and key to \
                        this file.", required=True)
    args = parser.parse_args()
    cert_hash = gen_cert(outfile=args.out)

    print("== Success!")
    print("Your certificate has been written to %s." % args.out)
    print("The cert's sha256-hash is:")
    print("    %s" % cert_hash)
