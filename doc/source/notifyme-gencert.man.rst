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

``notifyme-gencert`` ``-o OUTFILE``


DESCRIPTION
===========

Create a Private-public keypair for notify

OPTIONS
=======

-o file     path to write the output to.
--help      show help

EXAMPLES
===========

:notifyme-gencert -o cert.pem:
    create a public/private keypair and write it to lel.pem


BUGS
====

* None known so far. Drop me a mail if you find one!
