===================
 notifyme-collector
===================

---------------------------------------------
start a collector service for notifyme.
---------------------------------------------

:Author: Johannes Fürmann
:Date:   2013-11-09
:Copyright: AGPLv3
:Version: 0.1~dev1
:Manual section: 1
:Manual group: networking

SYNOPSIS
========

``notifyme-collector`` ``--help``

``notifyme-gencert`` ``-f configfile``

``notifyme-gencert`` ``-c configfile``


DESCRIPTION
===========

start a collector service for notifyme

OPTIONS
=======

-c          check a config file (no function yet)
-f          start notifyme-collector with this config file
--help      show help

EXAMPLES
===========

:notifyme-gencert -c config.yml:
    check config.yml for errors

:notifyme-gencert -f config.yml:
    staty notifyme with config.yml


BUGS
====

* None known so far. Drop me a mail if you find one!
