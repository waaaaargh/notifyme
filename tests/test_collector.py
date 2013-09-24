# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes

from unittest import TestCase

from notifyme.collector import CollectorProtocol
from notifyme.messages import NotificationMessage, ErrorMessage


class TestCollectorProtocol(TestCase):
    def test_collector_protocol(self):
        def test_callback(notification):
            self.assertIsInstance(notification, NotificationMessage)

        c = CollectorProtocol(notification_callback=test_callback)
        r = c(NotificationMessage(notification={}))
        self.assertIsNone(r)
        r = c(ErrorMessage("this should get me an error"))
        self.assertIs(type(r), ErrorMessage)
