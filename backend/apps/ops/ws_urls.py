"""
运维中心 WebSocket 路由。

由 config/asgi.py 统一聚合到全局 URLRouter；与 REST 路由
（/api/v1/ops/）对称，实时通道统一前缀 /ws/ops/。
"""

from django.urls import re_path

from apps.ops.consumers import TerminalConsumer

websocket_urlpatterns = [
    re_path(
        r"^ws/ops/terminal/(?P<host_id>[A-Za-z0-9_.-]+)/$",
        TerminalConsumer.as_asgi(),
    ),
]
