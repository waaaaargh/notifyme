=================
 notifyme-gencert
=================

---------------------------------------------
generate unix manpages from reStructured text
---------------------------------------------

:Author: Johannes Fürmann
:Date:   2013-11-06
:Copyright: AGPLv3
:Version: 0.1~dev1
:Manual section: 1
:Manual group: networking

SYNOPSIS
========

``notifyme-gencert`` ``--help``

``notifyme-gencert`` ``-g OUTFILE``

``notifyme-gencert`` ``-p CERTFILE``


DESCRIPTION
===========

Create a Private-public keypair for notify

OPTIONS
=======

-g file     generate certificate and write it to file
-p file     read the certificate from file and print it's SHA256 sum.
--help      show help

EXAMPLES
===========

:notifyme-gencert -g cert.pem:
    create a public/private keypair and write it to cert.pem

:notifyme-gencert -g cert.pem:
    read a certificate from cert.pem and write its sha256 hash to STDOUT


BUGS
====

* None known so far. Drop me a mail if you find one!
