"""
Langfuse API client for fetching session and trace data.
This module provides async functions to interact with the Langfuse API.
"""

import httpx
import base64
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from django.conf import settings


@dataclass
class Trace:
    """Data class representing a Langfuse trace."""
    id: str
    timestamp: str
    name: Optional[str]
    input: Optional[Dict[str, Any]]
    output: Optional[Dict[str, Any]]
    session_id: Optional[str]
    user_id: Optional[str]
    metadata: Optional[Dict[str, Any]]


@dataclass
class Session:
    """Data class representing a Langfuse session."""
    id: str
    created_at: str
    project_id: str
    environment: Optional[str]
    traces: List[Trace]


class LangfuseAPIError(Exception):
    """Custom exception for Langfuse API errors."""
    pass


class LangfuseClient:
    """Client for interacting with Langfuse API."""
    
    def __init__(self):
        self.public_key = settings.LANGFUSE_PUBLIC_KEY
        self.secret_key = settings.LANGFUSE_SECRET_KEY
        self.base_url = settings.LANGFUSE_API_BASE_URL
        
        if not self.public_key or not self.secret_key:
            raise LangfuseAPIError("Langfuse API credentials not configured in settings")
    
    def _get_auth_header(self) -> str:
        """Generate basic auth header for API requests."""
        auth_string = f"{self.public_key}:{self.secret_key}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"
    
    async def get_session(self, session_id: str) -> Session:
        """
        Fetch a session by ID from Langfuse API.
        
        Args:
            session_id (str): The unique identifier of the session
            
        Returns:
            Session: Session object with traces and metadata
            
        Raises:
            LangfuseAPIError: If API request fails or session not found
        """
        async with httpx.AsyncClient() as client:
            # Ensure proper URL construction
            base_url = self.base_url
            url = f"{base_url}/api/public/sessions/{session_id}"
            response = await client.get(
                url,
                headers={"Authorization": self._get_auth_header()}
            )
            
            if response.status_code == 404:
                raise LangfuseAPIError(f"Session not found: {session_id}")
            elif response.status_code != 200:
                raise LangfuseAPIError(f"Failed to fetch session: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Convert traces to Trace objects
            traces = []
            for trace_data in data.get('traces', []):
                trace = Trace(
                    id=trace_data.get('id'),
                    timestamp=trace_data.get('timestamp'),
                    name=trace_data.get('name'),
                    input=trace_data.get('input'),
                    output=trace_data.get('output'),
                    session_id=trace_data.get('sessionId'),
                    user_id=trace_data.get('userId'),
                    metadata=trace_data.get('metadata')
                )
                traces.append(trace)
            
            return Session(
                id=data['id'],
                created_at=data['createdAt'],
                project_id=data['projectId'],
                environment=data.get('environment'),
                traces=traces
            )


# Global client instance
langfuse_client = LangfuseClient()


async def get_session_by_id(session_id: str) -> Session:
    """
    Convenience function to fetch a session by ID.
    
    Args:
        session_id (str): The unique identifier of the session
        
    Returns:
        Session: Session object with traces and metadata
        
    Raises:
        LangfuseAPIError: If API request fails or session not found
    """
    return await langfuse_client.get_session(session_id)