import base64
from django.conf import settings


class LangfuseConfig:
    @property
    def public_key(self):
        return getattr(settings, 'LANGFUSE_PUBLIC_KEY', '')
    
    @property
    def secret_key(self):
        return getattr(settings, 'LANGFUSE_SECRET_KEY', '')
    
    @property
    def base_url(self):
        return getattr(settings, 'LANGFUSE_API_BASE_URL', 'https://us.cloud.langfuse.com')
    
    @property
    def auth_header(self):
        auth_string = f"{self.public_key}:{self.secret_key}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"


config = LangfuseConfig()