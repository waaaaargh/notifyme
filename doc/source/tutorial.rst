Installation
============

Debian
------

**Python Library**
  Download and install the packages::

    wget https://waaaaargh.github.com/notifyme/releases/python3-notifyme_0.1~dev1_all.deb
    sudo dpkg -i python3-notifyme_0.1~dev1_all.deb
    sudo apt-get install -f

  You're good to go!

**Collector**
  Again, the packaging scripts do most of the work (if you have already installed the python library)::

    wget https://waaaaargh.github.com/notifyme/releases/notifyme-collector_0.1~dev1_all.deb
    sudo dpkg -i notifyme-collector_0.1~dev1_all.deb

  And we're done wit the installation.

**Emitter**
  Installing the emitter is quite easy, too::

    wget https://waaaaargh.github.com/notifyme/releases/notifyme-emitter.1~dev1_all.deb
    sudo dpkg -i notifyme-emitter_0.1~dev1_all.deb


Other distributions
-------------------

**Python Library**
  Download the source tarball and install it via ``sudo setup.py install``

**Collector**
  You can simply create a server certificate for the collector::

    notifyme-gencert -g server_cert.pem

  Now copy the file ``collector.conf.yml`` from the source tarball. In the copy,
  edit the entries ``keyfile`` and ``certfile`` under each ``publisher`` and 
  ``collector`` to point at the absolute path of the certificate you just created.
  
  **WARNING**: If you use notifyme in production, you should **NOT** run
  ``notifyme-collector`` as root.

**Emitter**
  After you installed the python library, you can pretty much just use 
  ``bin/notifyme-emitter`` frpom the source tarball.



Configuration
=============

**Collector**
  The collector is the only component that needs explicit configuration
  at the moment.
  The YAML file that keeps the configuration has two main sections:
    * ``collector`` and
    * ``publisher``

  Each of those sections defines the network parameters of the respective
  components:

  ``address``
    address of the interface on which the component should listen

  ``port``
    port number on which the component should listen.

  ``keyfile/certfile``
    absolute path to the file with the X509 Key/Certificate

  ``permissions``
    Now this is where it gets a bit tricky:

    ``permission`` entries have the following atributes:
      * a `hash` that contains the SHA256 Sum of the client, and
      * a list of resources the client may subscribe/push to.

    This might look something like that::

       - hash:     bc5ed22b2c84d7968a769836711bfb8ca60cd1ef1156a6570e8f5fe724e077c1
         resources:
         - /foo
         - /bar

    You create certificates with the ``notifyme-gencert`` utility.
