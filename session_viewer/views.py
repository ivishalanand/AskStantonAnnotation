from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from core.langfuse.service import langfuse_service
from core.langfuse.exceptions import LangfuseAPIError
from core.session_parser import get_session_chat_data
from core.permissions import require_tool_permission

@login_required
@require_tool_permission('session_viewer')
def index(request):
    return render(request, 'session_viewer/index.html')


@login_required
@require_tool_permission('session_viewer')
def session_detail(request, session_id):
    """
    Display detailed view of a session with chat-like interface.
    
    Args:
        request: Django request object
        session_id: The unique identifier of the session to display
    """
    try:
        # Fetch session data using service layer
        session_data = langfuse_service.get_session(session_id)
        # Convert to Session object for parser compatibility
        from core.langfuse.models import Session
        session = Session(
            id=session_data['id'],
            created_at=session_data['createdAt'],
            updated_at=session_data.get('updatedAt', ''),
            project_id=session_data['projectId'],
            public=session_data.get('public', False),
            bookmarked=session_data.get('bookmarked', False),
            traces=session_data.get('traces', [])
        )
        
        # Parse session data into chat format
        chat_data = get_session_chat_data(session)
        
        context = {
            'session_id': session_id,
            'chat_data': chat_data,
            'error': None
        }
        
    except LangfuseAPIError as e:
        context = {
            'session_id': session_id,
            'chat_data': None,
            'error': str(e)
        }
    except Exception as e:
        context = {
            'session_id': session_id,
            'chat_data': None,
            'error': f"Unexpected error: {str(e)}"
        }
    
    return render(request, 'session_viewer/session_detail.html', context)