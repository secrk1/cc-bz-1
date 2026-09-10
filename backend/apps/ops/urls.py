"""运维中心 REST 路由，统一收口在 /api/v1/ops/ 前缀下。"""

from django.urls import path

from apps.ops.views.terminal_views import host_list

urlpatterns = [
    path("hosts", host_list, name="ops-host-list"),
]
