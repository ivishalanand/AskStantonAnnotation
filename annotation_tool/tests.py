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
        
        # Index view now redirects to queue_list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('annotation_tool:queue_list'))

    def test_authorized_user_can_access_annotation_tool(self):
        """Test that user with annotation permission can access tool."""
        self.client.login(username='annotator', password='testpass123')
        response = self.client.get(reverse('annotation_tool:index'))
        
        # Index view now redirects to queue_list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('annotation_tool:queue_list'))

    def test_unauthorized_user_cannot_access_annotation_tool(self):
        """Test that user without permission cannot access annotation tool."""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('annotation_tool:index'))
        
        # Should redirect to dashboard with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:dashboard'))

    def test_annotation_tool_queue_list_view(self):
        """Test that queue list view works correctly."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('annotation_tool:queue_list'))
        
        # Should return 200 even with API error (graceful degradation)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annotation Queues')

    def test_annotation_tool_queue_detail_view(self):
        """Test that queue detail view handles invalid queue gracefully."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('annotation_tool:queue_detail', kwargs={'queue_id': 'invalid-queue'}))
        
        # Should return 200 with error message (graceful error handling)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Queue Detail')


class AnnotationUtilsTests(TestCase):
    """Test cases for annotation tool utilities."""
    
    # Note: Auth header tests removed - now handled internally by the service layer

    def test_api_error_handling(self):
        """Test that API errors are handled gracefully."""
        from annotation_tool.utils import get_annotation_queues
        # Without proper credentials, should return error dict
        with self.settings(LANGFUSE_PUBLIC_KEY=None, LANGFUSE_SECRET_KEY=None):
            result = get_annotation_queues()
            self.assertTrue(result.get('error'))
            self.assertIn('message', result)
            self.assertEqual(result.get('data'), [])


class AnnotationModelTests(TestCase):
    """Test cases for annotation tool models."""
    
    def test_annotation_queue_from_api_data(self):
        """Test creating AnnotationQueue from API data."""
        from annotation_tool.models import AnnotationQueue
        
        api_data = {
            'id': 'test-queue-123',
            'name': 'Test Queue',
            'description': 'Test description',
            'createdAt': '2023-01-01T00:00:00.000Z',
            'updatedAt': '2023-01-02T00:00:00.000Z'
        }
        
        queue = AnnotationQueue.from_api_data(api_data)
        self.assertEqual(queue.queue_id, 'test-queue-123')
        self.assertEqual(queue.name, 'Test Queue')
        self.assertEqual(queue.description, 'Test description')
        self.assertTrue(queue.is_active)
        
    def test_annotation_queue_str_representation(self):
        """Test string representation of AnnotationQueue."""
        from annotation_tool.models import AnnotationQueue
        queue = AnnotationQueue(queue_id='test-123', name='Test Queue')
        self.assertEqual(str(queue), 'Test Queue (test-123)')
    
    def test_annotation_queue_item_from_api_data(self):
        """Test creating AnnotationQueueItem from API data."""
        from annotation_tool.models import AnnotationQueueItem
        
        api_data = {
            'id': 'item-123',
            'queueId': 'queue-123',
            'objectId': 'object-123',
            'objectType': 'TRACE',
            'status': 'PENDING',
            'createdAt': '2023-01-01T00:00:00.000Z',
            'updatedAt': '2023-01-02T00:00:00.000Z',
            'completedAt': None
        }
        
        item = AnnotationQueueItem.from_api_data(api_data)
        self.assertEqual(item.item_id, 'item-123')
        self.assertEqual(item.object_type, 'TRACE')
        self.assertEqual(item.status, 'PENDING')
        self.assertTrue(item.is_pending())
        self.assertFalse(item.is_completed())
        
    def test_annotation_queue_item_helper_methods(self):
        """Test helper methods on AnnotationQueueItem."""
        from annotation_tool.models import AnnotationQueueItem
        
        # Test completed item
        item = AnnotationQueueItem(status='COMPLETED')
        self.assertTrue(item.is_completed())
        self.assertFalse(item.is_pending())
        self.assertEqual(item.get_display_status(), 'Completed')
        
        # Test pending item
        item = AnnotationQueueItem(status='PENDING')
        self.assertFalse(item.is_completed())
        self.assertTrue(item.is_pending())
        self.assertEqual(item.get_display_status(), 'Pending')
        
        # Test object type display
        item = AnnotationQueueItem(object_type='TRACE')
        self.assertEqual(item.get_display_object_type(), 'Trace')


class AnnotationViewIntegrationTests(TestCase):
    """Integration tests for annotation views with mock API responses."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.superuser = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_superuser=True
        )
        self.superuser.must_change_password = False
        self.superuser.save()

    def test_queue_list_view_with_api_error(self):
        """Test queue list view handles API errors gracefully."""
        self.client.login(username='admin', password='testpass123')
        
        # This will trigger an API error due to missing credentials
        with self.settings(LANGFUSE_PUBLIC_KEY=None):
            response = self.client.get(reverse('annotation_tool:queue_list'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Annotation Queues')
            # Should show error message
            self.assertIn('error_message', response.context)

    def test_queue_detail_pagination(self):
        """Test queue detail view with pagination parameters."""
        self.client.login(username='admin', password='testpass123')
        
        # Test with page parameter
        response = self.client.get(
            reverse('annotation_tool:queue_detail', kwargs={'queue_id': 'test-queue'}) + '?page=2'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Queue Detail')

    def test_queue_model_methods(self):
        """Test additional queue model methods."""
        from annotation_tool.models import AnnotationQueue
        from datetime import datetime
        
        queue = AnnotationQueue(
            queue_id='test-123',
            name='Test Queue',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test to_dict method
        queue_dict = queue.to_dict()
        self.assertEqual(queue_dict['queue_id'], 'test-123')
        self.assertEqual(queue_dict['name'], 'Test Queue')
        
        # Test get_absolute_url
        expected_url = reverse('annotation_tool:queue_detail', kwargs={'queue_id': 'test-123'})
        self.assertEqual(queue.get_absolute_url(), expected_url)

    def test_queue_item_to_dict(self):
        """Test queue item to_dict method."""
        from annotation_tool.models import AnnotationQueueItem
        from datetime import datetime
        
        item = AnnotationQueueItem(
            item_id='item-123',
            queue_id='queue-123',
            object_id='obj-123',
            object_type='TRACE',
            status='PENDING',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        item_dict = item.to_dict()
        self.assertEqual(item_dict['item_id'], 'item-123')
        self.assertEqual(item_dict['object_type'], 'TRACE')
        self.assertEqual(item_dict['status'], 'PENDING')
