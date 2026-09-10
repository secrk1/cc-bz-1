"""
全局中间件：

- RequestIdMiddleware：全链路追踪 ID 的收口处。入站复用客户端
  ``X-Request-ID``（缺失则生成），写入 contextvar 并在响应头回传；
- GlobalExceptionMiddleware：兜底 DRF 之外抛出的异常，统一信封输出。
"""

import logging
import re
import uuid

from django.conf import settings
from django.http import JsonResponse
from rest_framework import status as http_status

from .context import set_request_id

logger = logging.getLogger(__name__)

# 仅放行可安全写入日志/响应头的字符，杜绝日志注入（换行、控制字符等）
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")
_REQUEST_ID_HEADER = "X-Request-ID"


def generate_request_id() -> str:
    return uuid.uuid4().hex


def normalize_incoming_id(raw: str | None) -> str:
    if raw and _SAFE_ID_RE.match(raw):
        return raw
    return generate_request_id()


class RequestIdMiddleware:
    """最外层中间件：最先执行、最后返回，覆盖整条请求链路。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inbound = request.headers.get(_REQUEST_ID_HEADER)
        request_id = normalize_incoming_id(inbound)
        request.request_id = request_id
        set_request_id(request_id)

        try:
            response = self.get_response(request)
        finally:
            # 无论成功或下游异常改写响应，contextvar 均已在本作用域生效
            pass

        response[_REQUEST_ID_HEADER] = request_id
        return response


class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:  # noqa: BLE001 — 全局兜底，必须一网打尽
            logger.exception("Unhandled exception on %s %s", request.method, request.path)
            from .context import get_request_id

            payload = {
                "code": 5000,
                "message": "服务器内部错误" if not settings.DEBUG else str(exc),
                "data": None,
                "request_id": get_request_id(),
            }
            response = JsonResponse(payload, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
            response[_REQUEST_ID_HEADER] = get_request_id()
            return response
