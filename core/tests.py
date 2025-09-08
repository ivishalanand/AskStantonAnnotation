"""
Test cases for the core app.
Tests dashboard functionality, permissions, and core utilities.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.http import HttpResponseRedirect
from core.permissions import user_has_tool_permission, assign_user_to_tool

User = get_user_model()


class DashboardViewTests(TestCase):
    """Test cases for the dashboard view and access control."""
    
    def setUp(self):
        """Set up test data for each test method."""
        self.client = Client()
        
        # Create test users
        self.superuser = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        # Set password change flag to False to avoid redirect
        self.superuser.must_change_password = False
        self.superuser.save()
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='testpass123'
        )
        # Set password change flag to False to avoid redirect
        self.regular_user.must_change_password = False
        self.regular_user.save()
        
        # Create permission groups
        self.annotation_group, _ = Group.objects.get_or_create(name='annotation_users')
        self.session_group, _ = Group.objects.get_or_create(name='session_viewers')

    def test_dashboard_requires_login(self):
        """Test that dashboard redirects to login for anonymous users."""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_access_for_authenticated_user(self):
        """Test dashboard access for authenticated user."""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, user!')

    def test_superuser_sees_all_tools(self):
        """Test that superuser can see all available tools."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annotation Tool')
        self.assertContains(response, 'Session Viewer')
        self.assertContains(response, 'You have access to 2 of 2')

    def test_regular_user_no_permissions(self):
        """Test that regular user without permissions sees no tools."""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have access to 0 of 2')
        self.assertContains(response, 'No Tools Available')

    def test_user_with_annotation_permission(self):
        """Test user with only annotation permission sees one tool."""
        # Add user to annotation group
        self.regular_user.groups.add(self.annotation_group)
        
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have access to 1 of 2')
        self.assertContains(response, 'Annotation Tool')

    def test_user_with_all_permissions(self):
        """Test user with all permissions sees all tools."""
        # Add user to both groups
        self.regular_user.groups.add(self.annotation_group, self.session_group)
        
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have access to 2 of 2')
        self.assertContains(response, 'Annotation Tool')
        self.assertContains(response, 'Session Viewer')


class PermissionUtilityTests(TestCase):
    """Test cases for permission utility functions."""
    
    def setUp(self):
        """Set up test data for permission tests."""
        self.superuser = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='testpass123'
        )
        
        # Create permission groups
        self.annotation_group, _ = Group.objects.get_or_create(name='annotation_users')
        self.session_group, _ = Group.objects.get_or_create(name='session_viewers')

    def test_superuser_has_all_permissions(self):
        """Test that superuser has access to all tools."""
        self.assertTrue(user_has_tool_permission(self.superuser, 'annotation'))
        self.assertTrue(user_has_tool_permission(self.superuser, 'session_viewer'))

    def test_regular_user_no_permissions(self):
        """Test that regular user without groups has no permissions."""
        self.assertFalse(user_has_tool_permission(self.regular_user, 'annotation'))
        self.assertFalse(user_has_tool_permission(self.regular_user, 'session_viewer'))

    def test_user_with_specific_permission(self):
        """Test user with specific group permission."""
        # Add user to annotation group
        self.regular_user.groups.add(self.annotation_group)
        
        self.assertTrue(user_has_tool_permission(self.regular_user, 'annotation'))
        self.assertFalse(user_has_tool_permission(self.regular_user, 'session_viewer'))

    def test_assign_user_to_tool_function(self):
        """Test the assign_user_to_tool utility function."""
        # Test valid tool assignment
        result = assign_user_to_tool(self.regular_user, 'annotation')
        self.assertTrue(result)
        self.assertTrue(user_has_tool_permission(self.regular_user, 'annotation'))
        
        # Test invalid tool assignment
        result = assign_user_to_tool(self.regular_user, 'invalid_tool')
        self.assertFalse(result)

    def test_invalid_tool_name(self):
        """Test permission checking with invalid tool name."""
        self.assertFalse(user_has_tool_permission(self.regular_user, 'invalid_tool'))
