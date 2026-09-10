"""
views 层：轻量分发 —— 入参初验、调用 Service、包装统一响应信封。

禁止在此编写事务与业务规则。
"""

from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from apps.cmdb.serializers import (
    EnvironmentSerializer,
    EnvironmentWriteSerializer,
)
from apps.cmdb.services import EnvironmentService
from core import responses


class EnvironmentViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = EnvironmentSerializer
    queryset = EnvironmentService.list_environments()

    def get_queryset(self):
        return EnvironmentService.list_environments(
            env_type=self.request.query_params.get("env_type"),
            status=self.request.query_params.get("status"),
            keyword=self.request.query_params.get("keyword"),
        )

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)
        data = self.paginator.get_paginated_response(serializer.data).data
        return responses.success(data)

    def retrieve(self, request, *args, **kwargs):
        env = EnvironmentService.get_environment(kwargs["pk"])
        return responses.success(EnvironmentSerializer(env).data)

    def create(self, request, *args, **kwargs):
        serializer = EnvironmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        env = EnvironmentService.create_environment(serializer.validated_data, request.user)
        return responses.success(
            EnvironmentSerializer(env).data,
            message="环境创建成功",
            http_status_code=http_status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        serializer = EnvironmentWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        env = EnvironmentService.update_environment(kwargs["pk"], serializer.validated_data)
        return responses.success(EnvironmentSerializer(env).data, message="环境更新成功")

    def destroy(self, request, *args, **kwargs):
        EnvironmentService.delete_environment(kwargs["pk"])
        return responses.success(message="环境已删除")

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        env = EnvironmentService.change_status(pk, "active")
        return responses.success(EnvironmentSerializer(env).data, message="环境已启用")

    @action(detail=True, methods=["post"])
    def maintain(self, request, pk=None):
        env = EnvironmentService.change_status(pk, "maintaining")
        return responses.success(EnvironmentSerializer(env).data, message="环境进入维护态")
