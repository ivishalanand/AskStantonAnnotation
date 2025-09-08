"""
Views for the session viewer app.
Provides session monitoring and management functionality.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from datetime import datetime, timezone
from core.permissions import require_tool_permission

# Get the User model
User = get_user_model()

@login_required
@require_tool_permission('session_viewer')
def index(request):
    """
    Main index view for the session viewer tool.
    Displays active Django sessions and basic session information.
    """
    
    # Get all active sessions
    active_sessions = Session.objects.filter(expire_date__gte=datetime.now(timezone.utc))
    
    # Prepare session data with user information
    session_data = []
    for session in active_sessions:
        # Decode session data to get user info
        session_dict = session.get_decoded()
        user_id = session_dict.get('_auth_user_id')
        
        # Get user if exists
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        session_info = {
            'session_key': session.session_key[:20] + '...' if len(session.session_key) > 20 else session.session_key,
            'full_session_key': session.session_key,
            'user': user,
            'expire_date': session.expire_date,
            'is_current': session.session_key == request.session.session_key,
            'session_data_keys': list(session_dict.keys()) if session_dict else []
        }
        session_data.append(session_info)
    
    # Sort by expire date (most recent first)
    session_data.sort(key=lambda x: x['expire_date'], reverse=True)
    
    # Context for template
    context = {
        'tool_name': 'Session Viewer',
        'description': 'Monitor and manage active user sessions',
        'total_sessions': len(session_data),
        'sessions': session_data,
        'current_session_key': request.session.session_key[:20] + '...',
        'features': [
            'View Active Sessions',
            'Monitor User Activity',
            'Session Data Analysis',
            'Security Monitoring',
            'Session Management Tools'
        ],
        'status': 'Active'
    }
    
    return render(request, 'session_viewer/index.html', context)
