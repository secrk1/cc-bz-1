"""
views 层：运行环境。五套标准环境由迁移种子初始化，仅允许维护性更新与状态流转。
"""

from rest_framework import status as http_status
from rest_framework.decorators import action

from apps.cmdb.serializers import EnvironmentSerializer, EnvironmentWriteSerializer
from apps.cmdb.services import EnvironmentService
from core import responses

from core.crud_views import BaseCrudViewSet


class EnvironmentViewSet(BaseCrudViewSet):
    service = EnvironmentService
    serializer_class = EnvironmentSerializer
    write_serializer_class = EnvironmentWriteSerializer
    created_message = "环境创建成功"
    updated_message = "环境更新成功"
    deleted_message = "环境已删除"

    def get_queryset(self):
        return EnvironmentService.list_environments(
            env_type=self.request.query_params.get("env_type"),
            status=self.request.query_params.get("status"),
            keyword=self.request.query_params.get("keyword"),
        )

    def service_create(self, payload, user):
        return EnvironmentService.create_environment(payload, created_by=user)

    def service_update(self, pk, payload):
        return EnvironmentService.update_environment(pk, payload)

    def service_delete(self, pk):
        EnvironmentService.delete_environment(pk)

    def create(self, request, *args, **kwargs):
        serializer = self.get_write_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        env = EnvironmentService.create_environment(
            dict(serializer.validated_data), request.user,
        )
        return responses.success(
            EnvironmentSerializer(env).data,
            message=self.created_message,
            http_status_code=http_status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        env = EnvironmentService.change_status(pk, "active")
        return responses.success(EnvironmentSerializer(env).data, message="环境已启用")

    @action(detail=True, methods=["post"])
    def maintain(self, request, pk=None):
        env = EnvironmentService.change_status(pk, "maintaining")
        return responses.success(EnvironmentSerializer(env).data, message="环境进入维护态")

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        env = EnvironmentService.change_status(pk, "inactive")
        return responses.success(EnvironmentSerializer(env).data, message="环境已停用")
