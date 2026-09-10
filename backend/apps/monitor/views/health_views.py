"""健康探针视图：只做分发与统一响应，探测逻辑全部在 Service 层。"""

from rest_framework import status as http_status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from apps.monitor.services.health_service import collect_health, collect_liveness
from core import responses


def _status_code(report: dict) -> int:
    return (
        http_status.HTTP_200_OK
        if report["status"] in ("healthy", "alive")
        else http_status.HTTP_503_SERVICE_UNAVAILABLE
    )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def healthz(request):
    """完整探针：实时探测 DB、Redis、Celery worker，供运维观测。"""
    report = collect_health(include_celery=True)
    return responses.success(report, http_status_code=_status_code(report))


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def readyz(request):
    """就绪探针：仅探测 DB 与 Redis，供容器编排健康检查。"""
    report = collect_health(include_celery=False)
    return responses.success(report, http_status_code=_status_code(report))


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def livez(request):
    """存活探针：进程可响应即可。"""
    report = collect_liveness()
    return responses.success(report, http_status_code=_status_code(report))
