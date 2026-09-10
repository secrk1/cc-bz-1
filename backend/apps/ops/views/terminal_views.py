"""运维中心轻量视图：主机清单查询，逻辑全部在 Service 层。"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.ops.services.host_service import list_hosts
from core import responses


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def host_list(request):
    hosts = list_hosts(
        env=request.query_params.get("env"),
        keyword=request.query_params.get("keyword"),
    )
    return responses.success({
        "items": hosts,
        "total": len(hosts),
        "online": sum(1 for h in hosts if h["status"] != "offline"),
    })
