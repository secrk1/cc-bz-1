"""
WSGI 入口 —— 供 gunicorn 等同步 WSGI 容器承载纯 REST 流量。

REST(WSGI) 与 WebSocket(ASGI/Daphne) 双协议栈共存：
- web 服务（gunicorn）使用本入口；
- daphne 服务使用 config.asgi:application。
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
