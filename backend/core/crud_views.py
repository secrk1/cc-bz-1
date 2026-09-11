"""
平台通用 DRF 基类：标准 CRUD 统一走响应信封，业务编排全部委托 Service。

任意领域子系统（cmdb / cicd / ...）的标准资源 ViewSet 均可继承本类，
只需声明：
- ``service``                  业务服务类（BaseCrudService 体系）
- ``serializer_class``         读序列化器
- ``write_serializer_class``   写序列化器（缺省与读一致）
- 覆写 ``service_create`` / ``service_update`` 以对接专用 Service 方法。

本类只做协议层事项（入参初验、分页、响应信封），禁止承载业务规则与事务。
"""

from rest_framework import status as http_status
from rest_framework.viewsets import ModelViewSet

from . import responses


class BaseCrudViewSet(ModelViewSet):
    service = None
    write_serializer_class = None
    created_message = "创建成功"
    updated_message = "更新成功"
    deleted_message = "删除成功"

    def get_write_serializer(self, *args, **kwargs):
        serializer_class = self.write_serializer_class or self.serializer_class
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))
        serializer = self.get_serializer(page, many=True)
        data = self.paginator.get_paginated_response(serializer.data).data
        return responses.success(data)

    def retrieve(self, request, *args, **kwargs):
        obj = self.service.get(kwargs["pk"])
        return responses.success(self.get_serializer(obj).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_write_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service_create(dict(serializer.validated_data), request.user)
        return responses.success(
            self.get_serializer(obj).data,
            message=self.created_message,
            http_status_code=http_status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        serializer = self.get_write_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service_update(kwargs["pk"], dict(serializer.validated_data))
        return responses.success(self.get_serializer(obj).data, message=self.updated_message)

    def destroy(self, request, *args, **kwargs):
        self.service_delete(kwargs["pk"])
        return responses.success(message=self.deleted_message)

    # -- Service 调用钩子，子类按需覆写 ---------------------------------------
    def service_create(self, payload: dict, user):
        return self.service.create(payload)

    def service_update(self, pk: int, payload: dict):
        return self.service.update(pk, payload)

    def service_delete(self, pk: int):
        self.service.delete(pk)
