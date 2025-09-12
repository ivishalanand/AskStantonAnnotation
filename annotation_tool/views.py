"""
Views for the annotation tool app.
Provides data annotation and labeling functionality.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.permissions import require_tool_permission
from core.langfuse.service import langfuse_service
from core.langfuse.exceptions import LangfuseAPIError
from core.session_parser import get_session_chat_data
from .utils import get_annotation_queues, get_annotation_queue, get_queue_items
from .models import AnnotationQueue, AnnotationQueueItem
import logging

logger = logging.getLogger(__name__)


@login_required
@require_tool_permission('annotation')
def index(request):
    """
    Main index view for the annotation tool.
    Redirects to the queue list view for better UX.
    """
    # Redirect to queue list - this provides better navigation experience
    return redirect(reverse('annotation_tool:queue_list'))


@login_required
@require_tool_permission('annotation')
def queue_list(request):
    """
    Display list of all annotation queues from Langfuse API.
    
    This view fetches queues from the Langfuse API and displays them
    in a card-based layout for easy navigation.
    """
    # Fetch queues from Langfuse API
    api_response = get_annotation_queues(page=1, limit=50)
    
    # Handle API errors gracefully
    if api_response.get('error'):
        logger.error(f"Failed to fetch annotation queues: {api_response['message']}")
        context = {
            'tool_name': 'Annotation Tool',
            'error_message': api_response['message'],
            'queues': [],
            'total_queues': 0
        }
    else:
        # Convert API data to model instances for easier template handling
        queues = []
        for queue_data in api_response.get('data', []):
            try:
                queue = AnnotationQueue.from_api_data(queue_data)
                queues.append(queue)
            except Exception as e:
                logger.warning(f"Failed to parse queue data: {e}")
                continue
        
        context = {
            'tool_name': 'Annotation Tool - Queues',
            'queues': queues,
            'total_queues': api_response.get('meta', {}).get('totalItems', 0),
            'page_info': api_response.get('meta', {})
        }
    
    return render(request, 'annotation_tool/queue_list.html', context)


@login_required
@require_tool_permission('annotation')
def queue_detail(request, queue_id):
    """
    Display detailed view of a specific annotation queue with paginated items.
    
    Args:
        queue_id (str): The unique identifier of the annotation queue
        
    This view shows queue information and a paginated table of queue items.
    """
    # Get current page from request, default to 1
    page_number = request.GET.get('page', 1)
    items_per_page = 20  # Fixed at 50 items per page as per MVP requirements
    
    # Fetch queue details from Langfuse API
    queue_data = get_annotation_queue(queue_id)
    
    # Handle API errors or missing queue
    if queue_data.get('error'):
        logger.error(f"Failed to fetch queue {queue_id}: {queue_data['message']}")
        context = {
            'tool_name': 'Annotation Tool - Queue Not Found',
            'error_message': queue_data['message'],
            'queue_id': queue_id,
            'queue': None,
            'items': [],
            'page_obj': None,
            'total_items': 0
        }
    else:
        try:
            # Convert API data to model instance
            queue = AnnotationQueue.from_api_data(queue_data)
            
            # Fetch paginated queue items from API
            try:
                page_number = int(page_number)
            except (ValueError, TypeError):
                page_number = 1
            
            items_response = get_queue_items(queue_id, page=page_number, limit=items_per_page)
            
            items = []
            page_obj = None
            total_items = 0
            
            if not items_response.get('error'):
                # Convert item data to model instances
                for item_data in items_response.get('data', []):
                    try:
                        item = AnnotationQueueItem.from_api_data(item_data)
                        items.append(item)
                    except Exception as e:
                        logger.warning(f"Failed to parse item data: {e}")
                        continue
                
                # Get pagination metadata from API response
                meta = items_response.get('meta', {})
                total_items = meta.get('totalItems', 0)
                current_page = meta.get('page', 1)
                total_pages = meta.get('totalPages', 1)
                
                # Create a simple page object for template use
                page_obj = {
                    'number': current_page,
                    'has_previous': current_page > 1,
                    'has_next': current_page < total_pages,
                    'previous_page_number': current_page - 1 if current_page > 1 else None,
                    'next_page_number': current_page + 1 if current_page < total_pages else None,
                    'paginator': {
                        'num_pages': total_pages,
                        'per_page': items_per_page,
                        'count': total_items
                    }
                }
            else:
                logger.warning(f"Failed to fetch items for queue {queue_id}: {items_response['message']}")
            
            context = {
                'tool_name': f'Annotation Tool - {queue.name}',
                'queue': queue,
                'queue_id': queue_id,
                'items': items,
                'page_obj': page_obj,
                'total_items': total_items,
                'items_per_page': items_per_page,
                'current_page': page_number
            }
            
        except Exception as e:
            logger.error(f"Failed to process queue data for {queue_id}: {e}")
            context = {
                'tool_name': 'Annotation Tool - Error',
                'error_message': f"Failed to load queue data: {str(e)}",
                'queue_id': queue_id,
                'queue': None,
                'items': [],
                'page_obj': None,
                'total_items': 0
            }
    
    return render(request, 'annotation_tool/queue_detail.html', context)


@login_required
@require_tool_permission('annotation')
def annotate_object(request, queue_id, object_type, object_id):
    """
    Display annotation interface for a specific queue item.
    
    Args:
        queue_id (str): The unique identifier of the annotation queue
        object_type (str): Type of object being annotated (session/trace)
        object_id (str): The unique identifier of the object to annotate
        
    For SESSION objects, displays the session chat data.
    For TRACE objects, shows placeholder content.
    """
    context = {
        'tool_name': f'Annotate {object_type.title()} - Admin Tools',
        'queue_id': queue_id,
        'object_type': object_type,
        'object_id': object_id,
        'chat_data': None,
        'error': None,
    }
    
    # Fetch and display session data for SESSION objects
    if object_type.lower() == 'session':
        try:
            # Fetch session data using service layer
            session_data = langfuse_service.get_session(object_id)
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
            context['chat_data'] = get_session_chat_data(session)
            
        except LangfuseAPIError as e:
            logger.error(f"Failed to fetch session {object_id}: {str(e)}")
            context['error'] = f"Failed to load session: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error fetching session {object_id}: {str(e)}")
            context['error'] = f"Unexpected error: {str(e)}"
    
    return render(request, 'annotation_tool/annotate_object.html', context)
