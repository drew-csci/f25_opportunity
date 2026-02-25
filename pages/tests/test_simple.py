from django.test import TestCase


class SimpleTest(TestCase):
    """Simple test to verify Django testing is working"""

    def test_basic_math(self):
        """Test that basic math works - simple example test"""
        self.assertEqual(1 + 1, 2)

    def test_string_operations(self):
        """Test that string operations work"""
        test_string = "Django"
        self.assertEqual(test_string.lower(), "django")
        self.assertTrue(test_string.startswith("D"))
