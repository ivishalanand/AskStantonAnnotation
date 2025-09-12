import asyncio
from functools import wraps
from typing import Any, Callable
from .services import AnnotationService, SessionService, ScoringService, TraceService


def sync_wrapper(async_func: Callable) -> Callable:
    """Wrapper to make async functions work in Django sync context"""
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(async_func(*args, **kwargs))
    return wrapper


class LangfuseService:
    """Main service class with sync wrappers for Django integration"""
    
    def __init__(self):
        self._annotation = AnnotationService()
        self._session = SessionService()
        self._scoring = ScoringService()
        self._trace = TraceService()
    
    # Annotation methods
    @sync_wrapper
    async def get_annotation_queues(self, page: int = 1, limit: int = None):
        return await self._annotation.get_queues(page, limit)
    
    @sync_wrapper
    async def get_annotation_queue(self, queue_id: str):
        return await self._annotation.get_queue(queue_id)
    
    @sync_wrapper
    async def get_queue_items(self, queue_id: str, status: str = None, page: int = 1, limit: int = None):
        return await self._annotation.get_queue_items(queue_id, status, page, limit)
    
    @sync_wrapper
    async def get_queue_item(self, queue_id: str, item_id: str):
        return await self._annotation.get_queue_item(queue_id, item_id)
    
    # Session methods
    @sync_wrapper
    async def get_session(self, session_id: str):
        return await self._session.get_session(session_id)
    
    # Scoring methods
    @sync_wrapper
    async def get_score_configs(self, page: int = 1, limit: int = None):
        return await self._scoring.get_score_configs(page, limit)
    
    @sync_wrapper
    async def create_score(self, trace_id: str, config_id: str, name: str, value: float, comment: str = None):
        return await self._scoring.create_score(trace_id, config_id, name, value, comment)
    
    @sync_wrapper
    async def create_trace_comment(self, trace_id: str, comment_text: str):
        return await self._scoring.create_trace_comment(trace_id, comment_text)
    
    @sync_wrapper
    async def create_session_comment(self, session_id: str, comment_text: str):
        return await self._scoring.create_session_comment(session_id, comment_text)
    
    # Trace methods
    @sync_wrapper
    async def get_trace(self, trace_id: str):
        return await self._trace.get_trace(trace_id)


# Global service instance
langfuse_service = LangfuseService()