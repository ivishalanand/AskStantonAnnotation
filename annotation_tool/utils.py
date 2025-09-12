"""
Langfuse API integration utilities for annotation tool.

This module provides helper functions to interact with the Langfuse API
for fetching annotation queues and related data.
"""

import logging
from typing import Dict, Any, Optional
from core.langfuse.service import langfuse_service
from core.langfuse.exceptions import LangfuseAPIError

logger = logging.getLogger(__name__)


def get_annotation_queues(page: int = 1, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for fetching annotation queues.
    Used in Django views that don't support async.
    
    Args:
        page (int): Page number, starts at 1
        limit (Optional[int]): Number of items per page
        
    Returns:
        Dict[str, Any]: API response or error dict
    """
    try:
        response = langfuse_service.get_annotation_queues(page, limit)
        return {
            'data': response.data,
            'meta': response.meta or {'page': page, 'limit': limit or 50, 'totalItems': 0, 'totalPages': 0}
        }
    except LangfuseAPIError as e:
        logger.error(f"Error getting annotation queues: {str(e)}")
        return {
            'error': True,
            'message': str(e),
            'data': [],
            'meta': {'page': page, 'limit': limit or 50, 'totalItems': 0, 'totalPages': 0}
        }


def get_annotation_queue(queue_id: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for fetching a specific annotation queue.
    
    Args:
        queue_id (str): Queue identifier
        
    Returns:
        Dict[str, Any]: Queue data or error dict
    """
    try:
        return langfuse_service.get_annotation_queue(queue_id)
    except LangfuseAPIError as e:
        logger.error(f"Error getting annotation queue {queue_id}: {str(e)}")
        return {
            'error': True,
            'message': str(e),
            'id': queue_id,
            'name': 'Queue Not Found',
            'description': None
        }


def get_queue_items(
    queue_id: str, 
    status: Optional[str] = None, 
    page: int = 1, 
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Synchronous wrapper for fetching queue items.
    
    Args:
        queue_id (str): Queue identifier
        status (Optional[str]): Status filter
        page (int): Page number
        limit (Optional[int]): Items per page
        
    Returns:
        Dict[str, Any]: Queue items or error dict
    """
    try:
        response = langfuse_service.get_queue_items(queue_id, status, page, limit)
        return {
            'data': response.data,
            'meta': response.meta or {'page': page, 'limit': limit or 50, 'totalItems': 0, 'totalPages': 0}
        }
    except LangfuseAPIError as e:
        logger.error(f"Error getting queue items for {queue_id}: {str(e)}")
        return {
            'error': True,
            'message': str(e),
            'data': [],
            'meta': {'page': page, 'limit': limit or 50, 'totalItems': 0, 'totalPages': 0}
        }


def test_api_connection() -> Dict[str, Any]:
    """
    Test the connection to Langfuse API.
    
    Returns:
        Dict[str, Any]: Test result with success status and details
    """
    try:
        result = get_annotation_queues(page=1, limit=1)
        
        if result.get('error'):
            return {
                'success': False,
                'message': f"API connection test failed: {result['message']}",
                'details': result
            }
        
        return {
            'success': True,
            'message': 'API connection successful',
            'queue_count': result.get('meta', {}).get('totalItems', 0),
            'details': result
        }
        
    except Exception as e:
        logger.error(f"API connection test failed: {str(e)}")
        return {
            'success': False,
            'message': f"API connection test failed: {str(e)}",
            'details': None
        }