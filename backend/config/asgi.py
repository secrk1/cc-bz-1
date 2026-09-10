"""
ASGI 入口（Daphne）—— HTTP 与 WebSocket 协议解耦分发。

路由规划：
- ``http``      -> Django 常规 URL 路由（RESTful API，复用根 urls.py）
- ``websocket`` -> URLRouter，聚合各领域应用的 ws_urls（当前仅运维中心终端通道）

新增实时通道时只需把对应应用的 websocket_urlpatterns 加入下面的聚合列表。
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

from apps.ops.ws_urls import websocket_urlpatterns as ops_ws_patterns  # noqa: E402
from core.ws import JwtAuthMiddlewareStack  # noqa: E402

# 全平台 WebSocket 路由聚合点（REST 路由在 config/urls.py 对称聚合）
websocket_urlpatterns = [
    *ops_ws_patterns,
]

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
