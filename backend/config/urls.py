"""
根路由：RESTful API 统一前缀 /api/v1/，按领域子系统解耦挂载。

严格规范：不引入、不挂载 django.contrib.admin.site.urls。
WebSocket 路由不在此文件声明，统一由 config/asgi.py 聚合各应用
ws_urls 后交由 ProtocolTypeRouter 分发，实现 REST 与 WS 的解耦。
"""

from django.urls import include, path

urlpatterns = [
    # core：仅技术横切（JWT 认证）
    path("api/v1/auth/", include("core.auth_urls")),
    # 领域子系统
    path("api/v1/monitor/", include("apps.monitor.urls")),
    path("api/v1/cmdb/", include("apps.cmdb.urls")),
    path("api/v1/ops/", include("apps.ops.urls")),
    path("api/v1/cicd/", include("apps.cicd.urls")),
]
