# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes

from unittest import TestCase

from notifyme.notification import Notification
from notifyme.collector import CollectorProtocol
from notifyme.messages import NotificationMessage, ErrorMessage

class TestCollectorProtocol(TestCase):
    def test_collector_protocol(self):
        class TestCallback:
            def __init__(self):
                self.called = False

            def __call__(self, arg1):
                self.called = True

        test_callback = TestCallback()
        c = CollectorProtocol(notification_callback=test_callback, allowed_resources=['/lel'])
        n = Notification(subject='lel', resource='/lel', urgency=88)
        r = c(NotificationMessage(n))
        self.assertIsNone(r)
        n = Notification(subject='lel', resource='/asdf', urgency=88)
        r = c(NotificationMessage(n))
        self.assertIsInstance(r, ErrorMessage)
        r = c(ErrorMessage("this should get me an error"))
        self.assertIs(type(r), ErrorMessage)
        self.assertTrue(test_callback.called)
