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
    
    async def create_trace_comment(self, trace_id: str, comment_text: str) -> dict:
        """Create a comment for a trace using the COMMENT-trace config."""
        return await self.create_score(
            trace_id=trace_id,
            config_id="cmfgu6usw000cad0740htzljh",
            name="COMMENT-trace",
            value=1,
            comment=comment_text
        )
    
    async def create_session_comment(self, session_id: str, comment_text: str) -> dict:
        """Create a comment for a session using the COMMENT-session config."""
        return await self.create_score(
            trace_id=session_id,
            config_id="cmfgu6usw000cad0740htzljh",  # Change it later with new config created for sessions.
            name="COMMENT-session",
            value=1,
            comment=comment_text
        )