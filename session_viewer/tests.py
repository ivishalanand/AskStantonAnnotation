"""
Test cases for the session viewer app.
Tests session viewer access, permissions, and session data display.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

User = get_user_model()


class SessionViewerViewTests(TestCase):
    """Test cases for session viewer views and functionality."""
    
    def setUp(self):
        """Set up test data for each test method."""
        self.client = Client()
        
        # Create test users with password change flag set to False
        self.superuser = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_superuser=True
        )
        self.superuser.must_change_password = False
        self.superuser.save()
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='testpass123'
        )
        self.regular_user.must_change_password = False
        self.regular_user.save()
        
        self.authorized_user = User.objects.create_user(
            username='session_admin',
            password='testpass123'
        )
        self.authorized_user.must_change_password = False
        self.authorized_user.save()
        
        # Create and assign permission group
        self.session_group, _ = Group.objects.get_or_create(name='session_viewers')
        self.authorized_user.groups.add(self.session_group)

    def test_session_viewer_requires_login(self):
        """Test that session viewer redirects to login for anonymous users."""
        response = self.client.get(reverse('session_viewer:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authorized_user_can_access_session_viewer(self):
        """Test that user with session viewer permission can access tool."""
        self.client.login(username='session_admin', password='testpass123')
        response = self.client.get(reverse('session_viewer:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Session Viewer')
        self.assertContains(response, 'Enter a session ID to view the conversation details')

    def test_unauthorized_user_cannot_access_session_viewer(self):
        """Test that user without permission cannot access session viewer."""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('session_viewer:index'))
        
        # Should redirect to dashboard with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:dashboard'))


