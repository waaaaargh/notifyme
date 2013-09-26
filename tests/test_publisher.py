# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes

from unittest import TestCase
from notifyme.messages import *
from notifyme.publisher import PublisherProtocol

class TestPublisher(TestCase):
    def test_publisher_protocol(self):
        p = PublisherProtocol(published_resources=['/test/'])
        m = p(None)
        self.assertIsInstance(m, PublishMessage)
        n = p(SubscribeMessage(subscribed_resources=['/test/']))
        self.assertIsInstance(n, ConfirmationMessage)

        p = PublisherProtocol(published_resources=['/test/'])
        m = p(None)
        self.assertIsInstance(m, PublishMessage)
        n = p(SubscribeMessage(subscribed_resources=['/wrong/']))
        self.assertIsInstance(n, ErrorMessage)
