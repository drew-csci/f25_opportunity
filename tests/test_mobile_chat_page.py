from django.test import TestCase
from django.urls import reverse

class MobileChatPageTest(TestCase):
    """
    Tests for the mobile chat page.
    """

    def test_simple_assertion(self):
        """
        A simple test to ensure the test runner is working.
        """
        self.assertEqual(1, 1)

    def test_mobile_chat_page_loads(self):
        """
        Tests that the mobile chat page is accessible.
        NOTE: You may need to replace 'mobile_chat_url_name' 
        with the actual URL name for your mobile chat page from your urls.py.
        """
        # Assuming you have a URL pattern named 'mobile_chat_url_name'
        # response = self.client.get(reverse('mobile_chat_url_name'))
        
        # If you don't use URL names, you can use the path directly.
        # This is less maintainable if your URLs change.
        response = self.client.get('/chat/mobile/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Mobile Chat")
