import httpx
from typing import Optional, Dict, Any
from .config import config
from .exceptions import LangfuseAPIError


class LangfuseClient:
    def __init__(self):
        self.base_url = config.base_url
        self.auth_header = config.auth_header
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/public{endpoint}",
                headers={"Authorization": self.auth_header},
                params=params or {}
            )
            return self._handle_response(response)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/public{endpoint}",
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json"
                },
                json=data or {}
            )
            return self._handle_response(response)
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = None
            raise LangfuseAPIError(
                f"API request failed: {response.status_code}",
                status_code=response.status_code,
                response_data=error_data
            )
        return response.json()