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
                 | (publisher) |
                 +-------------+
                        |
                        |
                        |
                        |
                       \|/
                 +-------------+
                 | notifymed   |
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
    | (publisher)          |             | (publisher) |
    +----------------------+             +-------------+
                |                              |
                +--------------+               |
                               |               |
                              \|/              |
                       +---------------+       |
                       | notifications |       |
                       | (collector)   |       |
                       +---------------+       |
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

So far, we had the following roles in our networks:
* a publisher that creates notification and feeds them into the network
* a subscriber that wants certain types of messages and gets them eventually
* a collector that simultaneously acts as subscriber and publisher and does some
  clever stuff in between, e.g. aggregate notifications, send out emails
  and so on.

Data model
----------

the main datatype in this model is of course the notification.

messages have:
* a `hostname` that identifies the machine which produced this notification
* a `resource`, which identifies the service that produced this notification
* a `time` field, that contains a unix timestamp indicating the time the
  notification was initially created.
* a `urgency`, an integer in the range of `0 <= urgency <= 99`
* a `subject`, a up to 256 characters long string that in few words describes
  what is going on and
* `data`, a free-form JSON object that has more information about the
  notification.

resources are part of a tree structure. There are two types of resources:
* sources, which can only be leaves in the resource structure and
* directories which can be leaves and parent nodes to sources and other
  directories.

Directories recursively aggregate all of their children.

An example tree structure might look like this:
```
weltraumpflege.org
+-- ~johannes
    +-- IRC
    +-- RSS
    +-- XMPP
+-- errorlogs
    +-- webapp1
    +-- webapp2
    ...
```

In this example, listing all messages from the resource `weltraumpflege.org/~johannes/`
would give me all the messages my IRC bouncer, my RSS aggregator and my XMPP
client produce.

Listing `weltraumpflege.org/errorlogs/webapp1` would give me only the errorlog
of `webapp1`.

The resource tree is constructed on the side of the subscriber or the 
collector.

Network Protocol
----------------

Messages are sent over the wire or the air as JSON objects wrapped in another
JSON Object for transport

The transport wrapper object contains the following information:
* `message_type`: Type of the message as String (up to 32 Characters)
* `message`: The message object as a String
* `signature`: The signature of the string in `message`.

### Message types

#### Notification

`Notification` object represented as a string, wrapped in a message object

#### Publish

List of JSON objects with the following properties:
* `published_resource`: resource string
* `description` description for the resource

#### Subscribe

List of JSON Objects with the following property
* `subscribed_resource`: resource string

#### Collect

List of JSON Objects with the following property
* `collected_resource`: resource string

### Protocol dialogues

#### Collector <-> Source
```
Collector: <collect message, '/test'>
Source: <push message, ...>
Source: <push message, ...>
[...]
```

#### Publisher <-> Subscriber
```
Publisher: <publish message, '/text'>
Subscriber: <subscribe message '/test'>
Publisher: <notification message, ...>
Publisher: <notification message, ...>
```
or
```
Publisher: <publish message, '/text'>
Subscriber: <subscribe message '/test'>
Publisher: <error message, 'resource not found'>
```
