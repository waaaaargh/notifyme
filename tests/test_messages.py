from unittest import TestCase

from notifyme.messages import *
from notifyme.notification import Notification

class TestMessageCreation(TestCase):
    def test_publish_message(self):
        p = PublishMessage(published_resources=['/test'])
        self.assertIsNotNone(p)
        self.assertRaises(ValueError,
                          PublishMessage,
                          {'published_resources': 'asdf'})
        self.assertRaises(ValueError,
                          PublishMessage,
                          {'published_resources': ['asdf', 1234]})
        self.assertIsNotNone(p.data)

    def test_subscribe_message(self):
        s = SubscribeMessage(subscribed_resources=['/test'])
        self.assertIsNotNone(s)
        self.assertRaises(ValueError,
                          SubscribeMessage,
                          {'subscribed_resources': 'asdf'})
        self.assertRaises(ValueError,
                          SubscribeMessage,
                          {'subscribed_resources': ['asdf', 1234]})

    def test_confirmation_message(self):
        c = ConfirmationMessage(confirmed_resources=['/test'])
        self.assertIsNotNone(c)
        self.assertRaises(ValueError,
                          ConfirmationMessage,
                          {'confirmed_resources': 'asdf'})
        self.assertRaises(ValueError,
                          ConfirmationMessage,
                          {'confirmed_resources': ['asdf', 1234]})

    def test_error_message(self):
        e = ErrorMessage(error_message="test")
        self.assertIsInstance(e, ProtocolMessage)
        self.assertIsInstance(e, ErrorMessage)

    def test_notification_message(self):
        n = Notification(data={}, subject='test', urgency=23,
                         resource='/test')
        nm = NotificationMessage(notification=n)
        self.assertIsInstance(nm, ProtocolMessage)
        self.assertIsInstance(nm, NotificationMessage)
        self.assertEquals(n.subject, nm.data['subject'])


class TestMessageParsing(TestCase):
    def test_publish_message(self):
        p = PublishMessage(published_resources=['/test'])
        w = WrappedProtocolMessage(message=p)
        p_new = WrappedProtocolMessage.parse(w.text)
        self.assertDictEqual(p.data, p_new.data)

    def test_subscribe_message(self):
        s = SubscribeMessage(subscribed_resources=['/test'])
        w = WrappedProtocolMessage(message=s)
        s_new = WrappedProtocolMessage.parse(w.text)
        self.assertDictEqual(s.data, s_new.data)

    def test_confirmation_message(self):
        c = ConfirmationMessage(confirmed_resources=['/test'])
        w = WrappedProtocolMessage(message=c)
        c_new = WrappedProtocolMessage.parse(w.text)
        self.assertDictEqual(c.data, c_new.data)

    def test_error_message(self):
        e = ErrorMessage(error_message="lel")
        w = WrappedProtocolMessage(message=e)
        e_new = WrappedProtocolMessage.parse(received_bytes=w.text)
        self.assertDictEqual(e.data, e_new.data)

    def test_notification_message(self):
        notification = Notification(resource='test', urgency=88, subject='lel',
                                    data={})
        n = NotificationMessage(notification)
        w = WrappedProtocolMessage(message=n)
        n_new = WrappedProtocolMessage.parse(w.text)
        self.assertDictEqual(n.data, n_new.data)
