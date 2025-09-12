from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class AnnotationQueue:
    id: str
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str
    project_id: str


@dataclass
class QueueItem:
    id: str
    queue_id: str
    object_id: str
    object_type: str
    status: str
    created_at: str
    updated_at: str


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
    id: str
    created_at: str
    updated_at: str
    project_id: str
    public: bool
    bookmarked: bool
    traces: List[Dict[str, Any]]  # Raw trace data from API


@dataclass
class ScoreConfig:
    id: str
    name: str
    description: Optional[str]
    data_type: str
    is_archived: bool
    project_id: str
    categories: Optional[List[Dict[str, Any]]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class APIResponse:
    data: Any
    meta: Optional[Dict[str, Any]] = None