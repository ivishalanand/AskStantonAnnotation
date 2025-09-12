from ..client import LangfuseClient
from ..models import Session


class SessionService:
    def __init__(self):
        self.client = LangfuseClient()
    
    async def get_session(self, session_id: str) -> Session:
        response = await self.client.get(f"/sessions/{session_id}")
        return response