# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes

from unittest import TestCase

from notifyme.subscriber import SubscriberProtocol
from notifyme.messages import PublishMessage, SubscribeMessage,\
    ConfirmationMessage, NotificationMessage


class TestSubscriberProtocol(TestCase):
    def test_subscriber_protocol(self):
        class CallbackTester:
            def __init__(self):
                self.called = None

            def __call__(self, notification):
                self.called = notification

        ctest = CallbackTester()

        p = SubscriberProtocol(notification_callback=ctest,
                               subscribed_resources=['/lel'])
        out_msg = p(PublishMessage(published_resources=['/lel']))
        self.assertIsInstance(out_msg, SubscribeMessage)
        out_msg = p(ConfirmationMessage(confirmed_resources=['/lel']))
        self.assertIsNone(out_msg)
        out_msg = p(NotificationMessage(notification_dict={}))
        self.assertIsNone(out_msg)
        self.assertIsNotNone(ctest.called)
