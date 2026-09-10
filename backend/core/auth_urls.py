"""
认证路由：标准 JWT Token 获取与刷新。

- POST /api/v1/auth/token/          获取 access + refresh
- POST /api/v1/auth/token/refresh/  刷新 access
"""

from django.urls import path

from .auth_views import NexusTokenObtainPairView, NexusTokenRefreshView

urlpatterns = [
    path("token/", NexusTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", NexusTokenRefreshView.as_view(), name="token_refresh"),
]
