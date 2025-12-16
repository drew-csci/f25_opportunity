from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User

class CompanyAboutAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company_user = User.objects.create_user(
            email='company@example.com',
            password='password123',
            user_type=User.UserType.ORGANIZATION,
            first_name='Company',
            last_name='User'
        )
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='password123',
            user_type=User.UserType.STUDENT,
            first_name='Student',
            last_name='User'
        )
        self.company_about_url = reverse('company_about')
        self.screen1_url = reverse('screen1')
        self.login_url = reverse('login')

    def test_anonymous_user_redirects_to_login(self):
        """
        Tests that an anonymous user is redirected to the login page
        when trying to access the company_about page.
        """
        response = self.client.get(self.company_about_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.company_about_url}')

    def test_non_company_user_redirects_to_screen1(self):
        """
        Tests that a logged-in non-organization user (e.g., student)
        is redirected to screen1 when trying to access the company_about page.
        """
        self.client.login(email='student@example.com', password='password123')
        response = self.client.get(self.company_about_url)
        self.assertRedirects(response, self.screen1_url)

    def test_company_user_can_access_company_about_page(self):
        """
        Tests that a logged-in organization user can successfully
        access the company_about page.
        """
        self.client.login(email='company@example.com', password='password123')
        response = self.client.get(self.company_about_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/company_about.html')
        self.assertContains(response, self.company_user.display_name)
        self.assertContains(response, "Our mission is to connect talented students")
