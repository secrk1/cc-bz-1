"""
JWT 认证视图。

在 simplejwt 标准响应（access/refresh）基础上注入 request_id，
使登录/续期接口同样可全链路追踪；响应头 X-Request-ID 由中间件统一设置。
"""

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .context import get_request_id


class NexusTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if isinstance(response.data, dict):
            response.data["request_id"] = get_request_id()
        return response


class NexusTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if isinstance(response.data, dict):
            response.data["request_id"] = get_request_id()
        return response
