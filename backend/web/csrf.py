"""
API 请求跳过 CSRF 验证。
API 使用 JWT Bearer Token 鉴权，不依赖 Cookie，因此 CSRF 保护不适用。
"""
from django.utils.deprecation import MiddlewareMixin


class APICSRFExemptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/api/'):
            request.csrf_processing_done = True
