from ..client import LangfuseClient


class TraceService:
    def __init__(self):
        self.client = LangfuseClient()
    
    async def get_trace(self, trace_id: str) -> dict:
        response = await self.client.get(f"/traces/{trace_id}")
        return response