from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import asyncio
from core.langfuse_client import get_session_by_id, LangfuseAPIError
from core.session_parser import get_session_chat_data


def index(request):
    return render(request, 'session_viewer/index.html')


@login_required
def session_detail(request, session_id):
    """
    Display detailed view of a session with chat-like interface.
    
    Args:
        request: Django request object
        session_id: The unique identifier of the session to display
    """
    try:
        # Fetch session data using async client
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session = loop.run_until_complete(get_session_by_id(session_id))
        loop.close()
        
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