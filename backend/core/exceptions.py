"""业务异常体系与 DRF 全局异常处理器。"""

from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

from .context import get_request_id
from .responses import (
    CODE_FORBIDDEN,
    CODE_NOT_FOUND,
    CODE_SERVER_ERROR,
    CODE_UNAUTHORIZED,
)


class BizException(Exception):
    """业务异常基类：Service 层主动抛出，由 DRF 处理器/中间件统一转信封。"""

    code = 4000
    http_status_code = http_status.HTTP_400_BAD_REQUEST
    message = "业务处理失败"

    def __init__(self, message: str | None = None, code: int | None = None,
                 http_status_code: int | None = None, data=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if http_status_code is not None:
            self.http_status_code = http_status_code
        self.data = data
        super().__init__(self.message)


class NotFoundError(BizException):
    code = CODE_NOT_FOUND
    http_status_code = http_status.HTTP_404_NOT_FOUND
    message = "资源不存在"


class UnauthorizedError(BizException):
    code = CODE_UNAUTHORIZED
    http_status_code = http_status.HTTP_401_UNAUTHORIZED
    message = "未认证或认证已失效"


class ForbiddenError(BizException):
    code = CODE_FORBIDDEN
    http_status_code = http_status.HTTP_403_FORBIDDEN
    message = "无操作权限"


def api_exception_handler(exc, context):
    """DRF 异常处理器：所有错误响应统一为信封结构并回传 request_id。"""
    if isinstance(exc, BizException):
        return Response(
            {
                "code": exc.code,
                "message": exc.message,
                "data": exc.data,
                "request_id": get_request_id(),
            },
            status=exc.http_status_code,
            headers={"X-Request-ID": get_request_id()},
        )

    response = drf_default_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and "detail" in detail:
            message = str(detail["detail"])
            data = None
        else:
            message = "请求参数校验失败"
            data = detail
        biz_code = _http_to_biz_code(response.status_code)
        response.data = {
            "code": biz_code,
            "message": message,
            "data": data,
            "request_id": get_request_id(),
        }
        response["X-Request-ID"] = get_request_id()
        return response

    # 未被 DRF 识别的异常交由中间件兜底
    return None


def _http_to_biz_code(http_code: int) -> int:
    if http_code == 401:
        return CODE_UNAUTHORIZED
    if http_code == 403:
        return CODE_FORBIDDEN
    if http_code == 404:
        return CODE_NOT_FOUND
    if http_code >= 500:
        return CODE_SERVER_ERROR
    return 4000
