====================
 notifyme-subscriber
====================

------------------------------------------------------------------
Subscribe to notifyme notifications and display them via libnotify
------------------------------------------------------------------

:Author: Johannes Fürmann
:Date:   2013-11-06
:Copyright: AGPLv3
:Version: 0.1~dev1
:Manual section: 1
:Manual group: networking

SYNOPSIS
========

``notifyme-subscriber`` ``--help``

``notifyme-subscriber`` ``-f CONFIGFILE``


DESCRIPTION
===========

Subscribe to notifyme notifications and display them via libnotify

OPTIONS
=======

-f CONFIGFILE   read CONFIGFILE as a config instead of 
                ``~/.notifyme-subscriber.conf.yaml``
--help          show help

EXAMPLES
===========

:notifyme-subscriber -f ~/subscriber.yaml:
    Start the notifyme subscriber with ~/subscriber.yaml as its
    config file.


BUGS
====

* None known so far. Drop me a mail if you find one!
