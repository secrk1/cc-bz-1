"""
全局统一 API 响应信封。

标准结构::

    {"code": int, "message": str, "data": Any, "request_id": str}

约定：
- ``code == 0`` 表示业务成功；非 0 为业务错误码（HTTP 状态码仍语义化保留）。
- ``request_id`` 由 RequestIdMiddleware 写入上下文，随每次响应回传，
  与响应头 ``X-Request-ID`` 一致，便于前后端日志串联排障。
- 所有 View 必须通过本模块的 ``success`` / ``error`` 返回，禁止裸 ``JsonResponse``。
"""

from typing import Any

from django.http import JsonResponse
from rest_framework import status as http_status

from .context import get_request_id

CODE_OK = 0
CODE_BIZ_ERROR = 4000
CODE_UNAUTHORIZED = 4001
CODE_FORBIDDEN = 4003
CODE_NOT_FOUND = 4004
CODE_SERVER_ERROR = 5000


def _envelope(code: int, message: str, data: Any = None) -> dict:
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": get_request_id(),
    }


def success(data: Any = None, message: str = "success",
            http_status_code: int = http_status.HTTP_200_OK) -> JsonResponse:
    return JsonResponse(_envelope(CODE_OK, message, data), status=http_status_code)


def error(message: str = "error", code: int = CODE_BIZ_ERROR,
          data: Any = None, http_status_code: int = http_status.HTTP_400_BAD_REQUEST) -> JsonResponse:
    return JsonResponse(_envelope(code, message, data), status=http_status_code)
