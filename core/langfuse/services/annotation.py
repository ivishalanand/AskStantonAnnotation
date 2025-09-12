from typing import Optional
from ..client import LangfuseClient
from ..models import AnnotationQueue, QueueItem, APIResponse


class AnnotationService:
    def __init__(self):
        self.client = LangfuseClient()
    
    async def get_queues(self, page: int = 1, limit: Optional[int] = None) -> APIResponse:
        params = {"page": page}
        if limit:
            params["limit"] = limit
        
        response = await self.client.get("/annotation-queues", params)
        return APIResponse(data=response.get("data", []), meta=response.get("meta"))
    
    async def get_queue(self, queue_id: str) -> AnnotationQueue:
        response = await self.client.get(f"/annotation-queues/{queue_id}")
        return response
    
    async def get_queue_items(
        self, 
        queue_id: str, 
        status: Optional[str] = None,
        page: int = 1,
        limit: Optional[int] = None
    ) -> APIResponse:
        params = {"page": page}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        
        response = await self.client.get(f"/annotation-queues/{queue_id}/items", params)
        return APIResponse(data=response.get("data", []), meta=response.get("meta"))
    
    async def get_queue_item(self, queue_id: str, item_id: str) -> QueueItem:
        response = await self.client.get(f"/annotation-queues/{queue_id}/items/{item_id}")
        return response