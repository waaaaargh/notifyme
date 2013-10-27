import unittest
from unittest import TestCase

class TestResourceHelpers(TestCase):
    def test_convert_to_path(self):
        from notifyme.resources import convert_to_path
        self.assertEqual(convert_to_path("/foo/bar"), ['foo', 'bar'])
        self.assertEqual(convert_to_path("/"), [])

    def test_valid_resource(self):
        from notifyme.resources import is_valid_resource
        self.assertTrue(is_valid_resource("/test/foo"))
        self.assertTrue(is_valid_resource("/test/"))
        self.assertTrue(is_valid_resource("/"))
        self.assertTrue(is_valid_resource("/äüöß"))
        self.assertTrue(is_valid_resource("/test"))
        self.assertFalse(is_valid_resource("test"))

    def test_is_subresource(self):
        from notifyme.resources import is_subresource
        self.assertTrue(is_subresource("/lel", "/"))
        self.assertTrue(is_subresource("/foo/bar", "/foo"))
        self.assertTrue(is_subresource("/foo/bar", "/foo/bar"))
        self.assertFalse(is_subresource("/foo", "/bar"))


if __name__ == '__main__':
    unittest.main()
