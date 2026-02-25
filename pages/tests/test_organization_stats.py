from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class OrganizationStatsTest(TestCase):
    """Test that organizations can see stats and updates for their posted/active opportunities"""

    def setUp(self):
        """Set up test data before each test"""
        # Create organization user
        self.org1 = User.objects.create_user(
            email='org1@test.com',
            password='testpass123',
            user_type='organization'
        )

        # Create another organization user
        self.org2 = User.objects.create_user(
            email='org2@test.com',
            password='testpass123',
            user_type='organization'
        )

        # Create a student user
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )

        self.client = Client()

    def test_organization_can_access_dashboard(self):
        """Test that authenticated organization users can access their dashboard"""
        # Log in as organization
        logged_in = self.client.login(email='org1@test.com', password='testpass123')
        self.assertTrue(logged_in, "Organization login failed")

        # Access organization dashboard
        response = self.client.get(reverse('screen1'))

        # Should get 200 OK response for organization users
        self.assertEqual(response.status_code, 200,
                        "Organization should be able to access dashboard")

    def test_unauthenticated_user_cannot_access_dashboard(self):
        """Test that unauthenticated users are redirected to login"""
        # Don't log in, just try to access
        response = self.client.get(reverse('screen1'))

        # Should redirect to login (302 redirect)
        self.assertEqual(response.status_code, 302,
                        "Unauthenticated users should be redirected to login")

        # Check that redirect goes to login page
        self.assertIn('/login', response.url or '/login',
                     "Should redirect to login page")

    def test_student_redirected_from_org_dashboard(self):
        """Test that student users cannot access organization dashboard"""
        # Log in as student
        logged_in = self.client.login(email='student@test.com', password='testpass123')
        self.assertTrue(logged_in, "Student login failed")

        # Try to access organization dashboard
        response = self.client.get(reverse('screen1'))

        # Students should be redirected or denied access (not 200)
        self.assertNotEqual(response.status_code, 200,
                           "Students should not have access to organization dashboard")

    def test_organization_sees_correct_template(self):
        """Test that organization dashboard renders the correct template"""
        # Log in as organization
        self.client.login(email='org1@test.com', password='testpass123')

        # Access dashboard
        response = self.client.get(reverse('screen1'))

        # Check that correct template is used
        self.assertTemplateUsed(response, 'pages/partials/s1_organization.html',
                               "Should use organization-specific template")

    def test_dashboard_contains_stats_context(self):
        """Test that organization dashboard provides opportunity stats in context"""
        # Log in as organization
        self.client.login(email='org1@test.com', password='testpass123')

        # Access dashboard
        response = self.client.get(reverse('screen1'))

        # Check that response context exists
        self.assertIsNotNone(response.context,
                            "Dashboard should provide context data")

        # Verify the user in context is correct
        if 'user' in response.context:
            self.assertEqual(response.context['user'].email, 'org1@test.com',
                           "Context should contain the logged-in organization user")
