"""
views 层：服务器预分配与组件实例。

预分配与实例创建的事务编排全部在 AllocationService 内完成，
View 仅做入参校验、调用与信封包装。
"""

from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.mixins import (
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from apps.cmdb.models import ComponentInstance
from apps.cmdb.serializers import (
    ComponentInstanceSerializer,
    InstanceCreateSerializer,
    InstanceStatusSerializer,
    PreAllocationCreateSerializer,
    PreAllocationSerializer,
)
from apps.cmdb.services import AllocationService
from core import responses


class PreAllocationViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin,
                          GenericViewSet):
    """服务器 -> 组件的预分配绑定（不支持整体 PUT 更新）。"""

    serializer_class = PreAllocationSerializer

    def get_queryset(self):
        params = self.request.query_params
        return AllocationService.list_allocations(
            server_id=params.get("server_id"),
            component_id=params.get("component_id"),
            environment_id=params.get("environment_id"),
            status=params.get("status"),
        )

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))
        data = self.paginator.get_paginated_response(
            self.get_serializer(page, many=True).data).data
        return responses.success(data)

    def retrieve(self, request, *args, **kwargs):
        allocation = AllocationService.get_allocation(kwargs["pk"])
        return responses.success(PreAllocationSerializer(allocation).data)

    def create(self, request, *args, **kwargs):
        serializer = PreAllocationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allocation = AllocationService.reserve(
            serializer.validated_data, operator=request.user,
        )
        return responses.success(
            PreAllocationSerializer(allocation).data,
            message="服务器预分配成功",
            http_status_code=http_status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        AllocationService.release(kwargs["pk"])
        return responses.success(message="预分配已释放")

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        allocation = AllocationService.release(pk)
        return responses.success(
            PreAllocationSerializer(allocation).data, message="预分配已释放")


class ComponentInstanceViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin,
                               GenericViewSet):
    """运行在服务器上的组件实例。"""

    serializer_class = ComponentInstanceSerializer

    def get_queryset(self):
        params = self.request.query_params
        return AllocationService.list_instances(
            server_id=params.get("server_id"),
            component_id=params.get("component_id"),
            environment_id=params.get("environment_id"),
            status=params.get("status"),
            keyword=params.get("keyword"),
        )

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))
        data = self.paginator.get_paginated_response(
            self.get_serializer(page, many=True).data).data
        return responses.success(data)

    def retrieve(self, request, *args, **kwargs):
        instance = AllocationService.get_instance(kwargs["pk"])
        return responses.success(ComponentInstanceSerializer(instance).data)

    def create(self, request, *args, **kwargs):
        serializer = InstanceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = AllocationService.create_instance(
            serializer.validated_data, operator=request.user,
        )
        return responses.success(
            ComponentInstanceSerializer(instance).data,
            message="组件实例创建成功",
            http_status_code=http_status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        AllocationService.delete_instance(kwargs["pk"])
        return responses.success(message="组件实例已删除")

    def _transition(self, request, pk, target_status):
        serializer = InstanceStatusSerializer(
            data={"target_status": target_status, **request.data})
        serializer.is_valid(raise_exception=True)
        instance = AllocationService.transition_instance(
            pk, target_status,
            operator=request.user,
            extra=serializer.validated_data.get("extra"),
        )
        return responses.success(ComponentInstanceSerializer(instance).data,
                                message=f"实例已{dict(ComponentInstance.Status.choices).get(target_status, target_status)}")

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        return self._transition(request, pk, ComponentInstance.Status.RUNNING)

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        return self._transition(request, pk, ComponentInstance.Status.STOPPED)

    @action(detail=True, methods=["post"])
    def abnormal(self, request, pk=None):
        return self._transition(request, pk, ComponentInstance.Status.ABNORMAL)
