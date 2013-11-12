=================
 notifyme-emitter
=================

---------------------------------------------
send notifyme notifications to a collector
---------------------------------------------

:Author: Johannes Fürmann
:Date:   2013-11-06
:Copyright: AGPLv3
:Version: 0.1~dev1
:Manual section: 1
:Manual group: networking

SYNOPSIS
========

``notifyme-emitter`` ``--help``

``notifyme-emitter`` ``-k KEYFILE`` ``-c CERTFILE`` ``-n HOSTNAME``
        ``-p PORTNUMBER`` ``-r RESOURCE`` ``-s SUBJECT`` ``[-u URGENCY]``
        ``[--serverhash SERVERHASH]``


DESCRIPTION
===========

Send notifyme notifications to a collector

OPTIONS
=======

--help           show help
-k KEYFILE       use KEYFILE as source for X509 Key
-c CERTFILE      use CERTFILE as source for X509 Certificate
-n HOSTNAME      connect to HOSTNAME
-p PORTNUMBER    connect to PORTNUMBER
-s SUBJECT       Subject of the notification to send
-u URGENCY       Urgency of the notification to send (1 <= URGENCY <= 100)
--serverhash HASH
                 SHA256 sum of the server's certificate. If this option is
                 used, the emitter will not connect to a server with another
                 certificate. Instead it will throw an error and exit.

BUGS
====

* None known so far. Drop me a mail if you find one!
