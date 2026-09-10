"""监控中心路由：统一挂在 /api/v1/monitor/ 前缀下。"""

from django.urls import path

from apps.monitor.views.health_views import healthz, livez, readyz

urlpatterns = [
    path("healthz", healthz, name="monitor-healthz"),
    path("healthz/ready", readyz, name="monitor-readyz"),
    path("healthz/live", livez, name="monitor-livez"),
]
