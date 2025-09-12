from typing import Optional
from ..client import LangfuseClient
from ..models import APIResponse


class ScoringService:
    def __init__(self):
        self.client = LangfuseClient()
    
    async def get_score_configs(self, page: int = 1, limit: Optional[int] = None) -> APIResponse:
        params = {"page": page}
        if limit:
            params["limit"] = limit
        
        response = await self.client.get("/score-configs", params)
        return APIResponse(data=response.get("data", []), meta=response.get("meta"))
    
    async def create_score(
        self,
        trace_id: str,
        config_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None
    ) -> dict:
        data = {
            "traceId": trace_id,
            "configId": config_id,
            "name": name,
            "value": value
        }
        if comment:
            data["comment"] = comment
        
        response = await self.client.post("/scores", data)
        return response
    
    async def create_comment(
        self,
        project_id: str,
        object_id: str,
        object_type: str,
        content: str,
        author_user_id: Optional[str] = None
    ) -> dict:
        data = {
            "projectId": project_id,
            "objectType": object_type,
            "objectId": object_id,
            "content": content
        }
        if author_user_id:
            data["authorUserId"] = author_user_id
        
        response = await self.client.post("/comments", data)
        return response