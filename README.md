NotifyMe...
===========

... is a simple solution for all your notification needs that might be spread
all across the internet on different servers and machines.

Use cases that NotifyMe is targeted at include:
* You have a torrent box somewhere and want to be notified if a torrent is
  ready
* You run XMPP and IRC clients on a remote machine (bouncer) and want to get
  notified if someone messages you, even if you're away from keyboard
* You return from a short trip to somewhere with no internet connectivity and
  want to read a clean backlog of the things that happened when you were away.
* You run a bunch of servers with two of your colleagues. Everyone of them
  should get an email when something goes wrong, but only the one on
  come-in-in-the-middle-of-the-night-when-shit-hits-the-fan-duty should get
  a text.

How does it work?
-----------------

On your network you have at least one service that runs all the time and
produces notifications from time to time. In the simplest case, you want to 
get those notifications on your desktop using simple libnotify popups. Then
your network would look like this:

```
                 +-------------+
                 | IRC bouncer |
                 | (pushclient)|
                 +-------------+
                        |
                        |
                        |
                        |
                       \|/
                 +-------------+
                 | notifymed   |
                 | (collector/ |
                 |  publisher) |
                 +-------------+
                        |
                        |
                        |
                        |
                       \|/
                 +-------------+
                 | desktop     |
                 |      client |
                 | (subscriber)|
                 +-------------+  
```

In a more complicated scenario, where you have two services that produce
messages, let's say one is your hackerspace's twitter account, and one is your
IRC bouncer. This time, you want your friend who is also on your hackerspace's
board, to get notifications whenever someone tweets about your hackerspace. In
this case, the whole setup looks like this:

```
    +----------------------+             +-------------+
    | @hackerspace twitter |             | IRC bouncer |
    | (pushclient          |             | (pushclient)|
    +----------------------+             +-------------+
                |                              |
                +--------------+               |
                               |               |
                              \|/              |
                       +---------------+<------+
                       | notifications |
                       | (collector)   |
                       +---------------+-------+
                               |               |
                               |               |
                               |               |
                      +--------+--------+      |
                     \|/               \|/    \|/
                +-----------+   +---------------+
                | your      |   | your          |
                |  friend's |   |   computer    |
                |  computer |   |               |
                | (subscri- |   |               |
                |  ber)     |   | (subscriber)  |
                +-----------+   +---------------+
```
The important thing here is that your friend can only read the notifications
that come from the Twitter account, whereas you also can read the notifications
from your IRC bouncer.


Components
----------
There are a few core components to a notifyme setup:
* The **publisher** can send notifications to subscribers. A publisher may 
  generate notifications on itself, or just forward or aggregate notifications
  it gets from other components or programs.
* In some situations opening a socket on a machine is not a viable option due
  to network and/or machine restrictions. That's where the **collector** comes
  in. It receives messages from a simple client prgram that processes or
  forwards them.
* The **push client** sends messages to a collector.
* The **subscriber** registers with a publisher and listens to messages.
