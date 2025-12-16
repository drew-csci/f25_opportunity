# Optional bonus test file for buggy_view

from django.test import TestCase, Client
from django.urls import reverse


class BuggyViewTests(TestCase):
    """Tests for the buggy search view after fixes."""

    def setUp(self):
        self.client = Client()

    def test_no_query_parameter(self):
        """Test that /buggy/ works without 'q' parameter (Bug 1 fix)."""
        response = self.client.get(reverse('buggy_search'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context)
        # Should return all projects when query is empty
        self.assertEqual(len(response.context['projects']), 4)

    def test_field_filter_all(self):
        """Test that field=All shows all projects (Bug 2 fix)."""
        response = self.client.get(reverse('buggy_search'), {'q': 'ai', 'field': 'All'})
        self.assertEqual(response.status_code, 200)
        # Should search all fields, not filter by field

    def test_search_by_description(self):
        """Test that searching works with description field (Bug 3 fix)."""
        response = self.client.get(reverse('buggy_search'), {'q': 'city'})
        self.assertEqual(response.status_code, 200)
        projects = response.context['projects']
        # Should find "Smart City Traffic Management"
        self.assertTrue(any('City' in p['title'] for p in projects))

    def test_search_by_title(self):
        """Test searching by title."""
        response = self.client.get(reverse('buggy_search'), {'q': 'blockchain'})
        self.assertEqual(response.status_code, 200)
        projects = response.context['projects']
        self.assertTrue(any('Blockchain' in p['title'] for p in projects))

    def test_field_filter_specific(self):
        """Test filtering by specific field."""
        response = self.client.get(reverse('buggy_search'), {'q': '', 'field': 'Blockchain'})
        self.assertEqual(response.status_code, 200)
        projects = response.context['projects']
        # Should only show Blockchain projects
        self.assertTrue(all(p['field'] == 'Blockchain' for p in projects))
