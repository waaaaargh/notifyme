# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes

from unittest import TestCase

from notifyme.notification import Notification
from notifyme.collector import CollectorProtocol
from notifyme.messages import NotificationMessage, ErrorMessage


class TestCollectorProtocol(TestCase):
    def test_collector_protocol(self):
        def test_callback(notification):
            self.assertIsInstance(notification, NotificationMessage)

        c = CollectorProtocol(notification_callback=test_callback,
                              allowed_resources=['/lel'])
        n = Notification(subject='lel', resource='/lel', urgency=88)
        r = c(NotificationMessage(n.to_dict))
        self.assertIsNone(r)
        n = Notification(subject='lel', resource='/asdf', urgency=88)
        r = c(NotificationMessage(n.to_dict))
        self.assertIsInstance(r, ErrorMessage)
        r = c(ErrorMessage("this should get me an error"))
        self.assertIs(type(r), ErrorMessage)
