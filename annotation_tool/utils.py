"""
Langfuse API integration utilities for annotation tool.

This module provides helper functions to interact with the Langfuse API
for fetching annotation queues and related data.
"""

import base64
import httpx
import asyncio
from typing import Optional, Dict, Any
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class LangfuseAPIError(Exception):
    """Custom exception for Langfuse API errors."""
    pass


def get_auth_header() -> str:
    """
    Generate Basic Authentication header for Langfuse API.
    
    Returns:
        str: Base64 encoded authentication header value
        
    Raises:
        LangfuseAPIError: If API credentials are not configured
    """
    public_key = getattr(settings, 'LANGFUSE_PUBLIC_KEY', None)
    secret_key = getattr(settings, 'LANGFUSE_SECRET_KEY', None)
    
    if not public_key or not secret_key:
        raise LangfuseAPIError("Langfuse API credentials not configured in settings")
    
    # Create Basic auth header
    auth_string = f"{public_key}:{secret_key}"
    auth_bytes = auth_string.encode('ascii')
    return base64.b64encode(auth_bytes).decode('ascii')


async def fetch_annotation_queues(page: int = 1, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Fetch all annotation queues from Langfuse API.
    
    Args:
        page (int): Page number, starts at 1 (default: 1)
        limit (Optional[int]): Number of items per page (default: API default)
        
    Returns:
        Dict[str, Any]: Response containing:
            - data: List of annotation queues
            - meta: Pagination metadata
            
    Raises:
        LangfuseAPIError: If API request fails
    """
    try:
        auth_header = get_auth_header()
        base_url = getattr(settings, 'LANGFUSE_API_BASE_URL', 'https://us.cloud.langfuse.com')
        url = f"{base_url}/api/public/annotation-queues"
        
        # Build query parameters
        params = {"page": page}
        if limit:
            params["limit"] = limit
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Basic {auth_header}"},
                params=params
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Langfuse API HTTP error: {e.response.status_code} - {e.response.text}")
        raise LangfuseAPIError(f"API request failed with status {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Langfuse API request error: {str(e)}")
        raise LangfuseAPIError(f"Failed to connect to Langfuse API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching annotation queues: {str(e)}")
        raise LangfuseAPIError(f"Unexpected error: {str(e)}")


async def fetch_annotation_queue(queue_id: str) -> Dict[str, Any]:
    """
    Fetch a specific annotation queue by ID.
    
    Args:
        queue_id (str): The unique identifier of the annotation queue
        
    Returns:
        Dict[str, Any]: Queue details including id, name, description, scoreConfigIds, etc.
        
    Raises:
        LangfuseAPIError: If API request fails
    """
    try:
        auth_header = get_auth_header()
        base_url = getattr(settings, 'LANGFUSE_API_BASE_URL', 'https://us.cloud.langfuse.com')
        url = f"{base_url}/api/public/annotation-queues/{queue_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Basic {auth_header}"}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise LangfuseAPIError(f"Annotation queue '{queue_id}' not found")
        logger.error(f"Langfuse API HTTP error: {e.response.status_code} - {e.response.text}")
        raise LangfuseAPIError(f"API request failed with status {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Langfuse API request error: {str(e)}")
        raise LangfuseAPIError(f"Failed to connect to Langfuse API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching annotation queue {queue_id}: {str(e)}")
        raise LangfuseAPIError(f"Unexpected error: {str(e)}")


async def fetch_queue_items(
    queue_id: str, 
    status: Optional[str] = None, 
    page: int = 1, 
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Fetch items for a specific annotation queue.
    
    Args:
        queue_id (str): The unique identifier of the annotation queue
        status (Optional[str]): Filter by status (e.g., "PENDING", "COMPLETED")
        page (int): Page number, starts at 1 (default: 1)
        limit (Optional[int]): Number of items per page
        
    Returns:
        Dict[str, Any]: Response containing:
            - data: Array of AnnotationQueueItems
            - meta: Pagination metadata
            
    Raises:
        LangfuseAPIError: If API request fails
    """
    try:
        auth_header = get_auth_header()
        base_url = getattr(settings, 'LANGFUSE_API_BASE_URL', 'https://us.cloud.langfuse.com')
        url = f"{base_url}/api/public/annotation-queues/{queue_id}/items"
        
        # Build query parameters
        params = {"page": page}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Basic {auth_header}"},
                params=params
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise LangfuseAPIError(f"Annotation queue '{queue_id}' not found")
        logger.error(f"Langfuse API HTTP error: {e.response.status_code} - {e.response.text}")
        raise LangfuseAPIError(f"API request failed with status {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Langfuse API request error: {str(e)}")
        raise LangfuseAPIError(f"Failed to connect to Langfuse API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching queue items for {queue_id}: {str(e)}")
        raise LangfuseAPIError(f"Unexpected error: {str(e)}")


# Synchronous wrappers for Django views
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
        return asyncio.run(fetch_annotation_queues(page, limit))
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
        return asyncio.run(fetch_annotation_queue(queue_id))
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
        return asyncio.run(fetch_queue_items(queue_id, status, page, limit))
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
        # Try to fetch first page of queues with minimal data
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