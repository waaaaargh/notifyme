What is notifyme?
=================

Notifyme is a python library that helps you transport and manage realtime
notifications securely. It also comes with exemplary implementations for
most of the components that are ready-to-use.

Meet the core components
------------------------

Emitter
  Generates notifications and forwards it to the collector.

Collector
  The collector aggregates notifications from emitters and forwards them to
  a publisher

Publisher
  The Publisher either generates notifications itself or distributes
  notifications that the collector aggregates to connectet subscribers.

Subscriber
  A subscriber is a program that listens to notifications and reacts to them,
  i.e. presents it to the user.

Security
--------

All components communicate with each other mutually authenticated and
encrypted. This ensures that a user does not get forged notifications 
and that notifications cannot be read if the network between the com-
ponents is being monitored or even compromised.
