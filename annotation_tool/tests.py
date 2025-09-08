"""
Test cases for the annotation tool app.
Tests annotation tool access, permissions, and functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

User = get_user_model()


class AnnotationToolViewTests(TestCase):
    """Test cases for annotation tool views and access control."""
    
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
            username='annotator',
            password='testpass123'
        )
        self.authorized_user.must_change_password = False
        self.authorized_user.save()
        
        # Create and assign permission group
        self.annotation_group, _ = Group.objects.get_or_create(name='annotation_users')
        self.authorized_user.groups.add(self.annotation_group)

    def test_annotation_tool_requires_login(self):
        """Test that annotation tool redirects to login for anonymous users."""
        response = self.client.get(reverse('annotation_tool:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_superuser_can_access_annotation_tool(self):
        """Test that superuser can access annotation tool."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('annotation_tool:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annotation Tool')
        self.assertContains(response, 'Hello World!')

    def test_authorized_user_can_access_annotation_tool(self):
        """Test that user with annotation permission can access tool."""
        self.client.login(username='annotator', password='testpass123')
        response = self.client.get(reverse('annotation_tool:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annotation Tool')
        self.assertContains(response, 'Data annotation and labeling platform')

    def test_unauthorized_user_cannot_access_annotation_tool(self):
        """Test that user without permission cannot access annotation tool."""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('annotation_tool:index'))
        
        # Should redirect to dashboard with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:dashboard'))

    def test_annotation_tool_displays_correct_context(self):
        """Test that annotation tool displays correct template context."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('annotation_tool:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annotation Tool')
        self.assertContains(response, 'Data Import and Export')
        self.assertContains(response, 'Multiple Annotation Types')
        self.assertContains(response, 'Under Development')

    def test_annotation_tool_shows_planned_features(self):
        """Test that annotation tool displays planned features."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('annotation_tool:index'))
        
        self.assertEqual(response.status_code, 200)
        # Check for planned features
        self.assertContains(response, 'User Management and Assignments')
        self.assertContains(response, 'Progress Tracking and Analytics')
        self.assertContains(response, 'Quality Control and Review Workflow')
