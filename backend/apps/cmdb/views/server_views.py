"""views 层：服务器资产（规格 / IP / 环境 / 运行状态）。"""

from rest_framework.decorators import action

from apps.cmdb.models import Server
from apps.cmdb.serializers import ServerSerializer, ServerWriteSerializer
from apps.cmdb.services import ServerService
from core import responses

from core.crud_views import BaseCrudViewSet


class ServerViewSet(BaseCrudViewSet):
    service = ServerService
    serializer_class = ServerSerializer
    write_serializer_class = ServerWriteSerializer
    created_message = "服务器纳管成功"
    updated_message = "服务器更新成功"
    deleted_message = "服务器已下线删除"

    def get_queryset(self):
        params = self.request.query_params
        return ServerService.list_servers(
            environment_id=params.get("environment_id")
            or params.get("environment"),
            status=params.get("status"),
            provider=params.get("provider"),
            hostname=params.get("hostname"),
            ip_address=params.get("ip_address"),
            keyword=params.get("keyword"),
        )

    def service_create(self, payload, user):
        return ServerService.create_server(payload, owner=user)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        server = ServerService.change_status(pk, Server.Status.RUNNING)
        return responses.success(ServerSerializer(server).data, message="服务器已置为运行中")

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        server = ServerService.change_status(pk, Server.Status.STOPPED)
        return responses.success(ServerSerializer(server).data, message="服务器已停机")

    @action(detail=True, methods=["post"])
    def maintain(self, request, pk=None):
        server = ServerService.change_status(pk, Server.Status.MAINTAINING)
        return responses.success(ServerSerializer(server).data, message="服务器进入维护态")

    @action(detail=True, methods=["post"])
    def abnormal(self, request, pk=None):
        server = ServerService.change_status(pk, Server.Status.ABNORMAL)
        return responses.success(ServerSerializer(server).data, message="服务器已标记异常")

    @action(detail=True, methods=["post"])
    def retire(self, request, pk=None):
        server = ServerService.change_status(pk, Server.Status.RETIRED)
        return responses.success(ServerSerializer(server).data, message="服务器已下线")
