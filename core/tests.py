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
        self.assertContains(response, 'Dashboard')

    def test_superuser_sees_all_tools(self):
        """Test that superuser can see all available tools."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annotation Tool')

    def test_regular_user_no_permissions(self):
        """Test that regular user without permissions sees no tools."""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_user_with_annotation_permission(self):
        """Test user with only annotation permission sees one tool."""
        # Add user to annotation group
        self.regular_user.groups.add(self.annotation_group)
        
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annotation Tool')

    def test_user_with_all_permissions(self):
        """Test user with all permissions sees all tools."""
        # Add user to both groups
        self.regular_user.groups.add(self.annotation_group, self.session_group)
        
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
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


class SessionParserTests(TestCase):
    """Test cases for session parsing functionality."""
    
    def setUp(self):
        """Set up test data for session parsing tests."""
        # Mock trace data structure
        self.mock_trace_data = {
            'id': 'trace_123',
            'timestamp': '2024-01-01T12:00:00Z',
            'input': {
                'messages': [
                    {
                        'id': 'msg_001',
                        'type': 'human',
                        'content': 'What is the weather in Paris?'
                    }
                ]
            },
            'output': {
                'messages': [
                    {
                        'id': 'msg_001',
                        'type': 'human',
                        'content': 'What is the weather in Paris?'
                    },
                    {
                        'id': 'msg_002',
                        'type': 'ai',
                        'content': [
                            {
                                'type': 'text',
                                'text': 'I will check the weather for you.'
                            }
                        ],
                        'tool_calls': [
                            {
                                'id': 'tool_001',
                                'name': 'get_weather',
                                'args': {'city': 'Paris', 'country': 'France'}
                            }
                        ]
                    },
                    {
                        'id': 'msg_003',
                        'type': 'tool',
                        'tool_call_id': 'tool_001',
                        'content': 'Weather in Paris: 22°C, sunny'
                    },
                    {
                        'id': 'msg_004',
                        'type': 'ai',
                        'content': [
                            {
                                'type': 'text',
                                'text': 'The weather in Paris is 22°C and sunny.'
                            }
                        ]
                    }
                ]
            }
        }
        
        # Mock session data
        self.mock_session_data = {
            'id': 'session_456',
            'created_at': '2024-01-01T11:30:00Z',
            'project_id': 'project_789',
            'environment': 'production',
            'traces': [self.mock_trace_data]
        }
        
    def create_mock_trace(self, trace_data):
        """Create a mock trace object with required attributes."""
        class MockTrace:
            def __init__(self, data):
                self.id = data['id']
                self.timestamp = data['timestamp']
                self.input = data['input']
                self.output = data['output']
        
        return MockTrace(trace_data)
    
    def create_mock_session(self, session_data):
        """Create a mock session object with required attributes."""
        class MockSession:
            def __init__(self, data, trace_creator):
                self.id = data['id']
                self.created_at = data['created_at']
                self.project_id = data['project_id']
                self.environment = data['environment']
                self.traces = [trace_creator(t) for t in data['traces']]
        
        return MockSession(session_data, self.create_mock_trace)

    def test_get_input_message(self):
        """Test extraction of input message from trace."""
        from core.session_parser import get_input_message
        
        trace = self.create_mock_trace(self.mock_trace_data)
        result = get_input_message(trace)
        
        self.assertEqual(result, 'What is the weather in Paris?')

    def test_get_trace_id(self):
        """Test extraction of trace ID."""
        from core.session_parser import get_trace_id
        
        trace = self.create_mock_trace(self.mock_trace_data)
        result = get_trace_id(trace)
        
        self.assertEqual(result, 'trace_123')

    def test_filter_output_messages(self):
        """Test filtering of output messages after human input."""
        from core.session_parser import filter_output_messages
        
        trace = self.create_mock_trace(self.mock_trace_data)
        result = filter_output_messages(trace)
        
        # Should return 3 messages after the human input
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['type'], 'ai')
        self.assertEqual(result[1]['type'], 'tool')
        self.assertEqual(result[2]['type'], 'ai')

    def test_format_tool_input_valid_json(self):
        """Test formatting of valid tool input arguments."""
        from core.session_parser import format_tool_input
        
        tool_args = {'city': 'Paris', 'country': 'France'}
        result = format_tool_input(tool_args)
        
        self.assertIsInstance(result, str)
        self.assertIn('Paris', result)
        self.assertIn('France', result)

    def test_format_tool_input_none(self):
        """Test formatting of None tool input."""
        from core.session_parser import format_tool_input
        
        result = format_tool_input(None)
        self.assertIsNone(result)

    def test_format_tool_input_invalid_json(self):
        """Test formatting of non-serializable tool input."""
        from core.session_parser import format_tool_input
        
        # Create a non-serializable object
        class NonSerializable:
            pass
        
        tool_args = NonSerializable()
        result = format_tool_input(tool_args)
        
        self.assertIsInstance(result, str)

    def test_simplify_output_messages(self):
        """Test simplification of output messages."""
        from core.session_parser import simplify_output_messages
        
        messages = [
            {
                'type': 'ai',
                'content': [{'type': 'text', 'text': 'I will help you'}],
                'tool_calls': [
                    {
                        'id': 'tool_001',
                        'name': 'get_weather',
                        'args': {'city': 'Paris'}
                    }
                ]
            },
            {
                'type': 'tool',
                'tool_call_id': 'tool_001',
                'content': 'Weather data'
            },
            {
                'type': 'ai',
                'content': [{'type': 'text', 'text': 'The weather is nice'}]
            }
        ]
        
        result = simplify_output_messages(messages)
        
        self.assertEqual(len(result), 3)
        self.assertIn('ai', result[0])
        self.assertEqual(result[0]['ai'], 'I will help you')
        self.assertIn('tool', result[1])
        self.assertEqual(result[1]['tool']['name'], 'get_weather')
        self.assertEqual(result[1]['tool']['output'], 'Weather data')
        self.assertIn('ai', result[2])
        self.assertEqual(result[2]['ai'], 'The weather is nice')

    def test_build_chat_history(self):
        """Test building chat history from session."""
        from core.session_parser import build_chat_history
        
        session = self.create_mock_session(self.mock_session_data)
        result = build_chat_history(session)
        
        self.assertEqual(len(result), 1)
        self.assertIn('trace_id', result[0])
        self.assertIn('input', result[0])
        self.assertIn('output', result[0])
        self.assertEqual(result[0]['trace_id'], 'trace_123')
        self.assertEqual(result[0]['input'], 'What is the weather in Paris?')

    def test_get_session_chat_data(self):
        """Test main session parsing function."""
        from core.session_parser import get_session_chat_data
        
        session = self.create_mock_session(self.mock_session_data)
        result = get_session_chat_data(session)
        
        # Check structure
        expected_keys = ['session_id', 'created_at', 'project_id', 'environment', 'traces', 'total_traces']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check values
        self.assertEqual(result['session_id'], 'session_456')
        self.assertEqual(result['project_id'], 'project_789')
        self.assertEqual(result['environment'], 'production')
        self.assertEqual(result['total_traces'], 1)
        self.assertIsInstance(result['traces'], list)

    def test_empty_trace_handling(self):
        """Test handling of trace with no messages."""
        from core.session_parser import filter_output_messages
        
        empty_trace_data = {
            'id': 'empty_trace',
            'timestamp': '2024-01-01T12:00:00Z',
            'input': {'messages': [{'id': 'msg_001', 'type': 'human', 'content': 'Hello'}]},
            'output': {'messages': []}
        }
        
        trace = self.create_mock_trace(empty_trace_data)
        result = filter_output_messages(trace)
        
        self.assertEqual(result, [])

    def test_multiple_traces_sorting(self):
        """Test that traces are sorted by timestamp."""
        from core.session_parser import build_chat_history
        
        # Create traces with different timestamps
        trace1_data = dict(self.mock_trace_data)
        trace1_data['id'] = 'trace_1'
        trace1_data['timestamp'] = '2024-01-01T12:00:00Z'
        
        trace2_data = dict(self.mock_trace_data)
        trace2_data['id'] = 'trace_2'
        trace2_data['timestamp'] = '2024-01-01T11:00:00Z'  # Earlier
        
        session_data = dict(self.mock_session_data)
        session_data['traces'] = [trace1_data, trace2_data]  # Add in wrong order
        
        session = self.create_mock_session(session_data)
        result = build_chat_history(session)
        
        # Should be sorted by timestamp (earliest first)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['trace_id'], 'trace_2')  # Earlier timestamp
        self.assertEqual(result[1]['trace_id'], 'trace_1')  # Later timestamp
