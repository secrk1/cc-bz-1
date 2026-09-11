"""views 层：应用领域四层（系统域 / 应用系统 / 应用 / 组件），仅做分发。"""

from rest_framework.decorators import action

from apps.cmdb.serializers import (
    AppComponentListSerializer,
    AppComponentSerializer,
    AppComponentWriteSerializer,
    ApplicationListSerializer,
    ApplicationSerializer,
    ApplicationWriteSerializer,
    AppSystemListSerializer,
    AppSystemSerializer,
    AppSystemWriteSerializer,
    SystemDomainSerializer,
    SystemDomainWriteSerializer,
)
from apps.cmdb.services import (
    AppComponentService,
    ApplicationService,
    AppSystemService,
    SystemDomainService,
)
from core import responses

from core.crud_views import BaseCrudViewSet


class SystemDomainViewSet(BaseCrudViewSet):
    """系统域：GET 列表/详情、POST、PUT/PATCH、DELETE。"""

    service = SystemDomainService
    serializer_class = SystemDomainSerializer
    write_serializer_class = SystemDomainWriteSerializer
    created_message = "系统域创建成功"
    updated_message = "系统域更新成功"
    deleted_message = "系统域已删除"

    def get_queryset(self):
        return self.service.list_domains(
            status=self.request.query_params.get("status"),
            keyword=self.request.query_params.get("keyword"),
        )


class AppSystemViewSet(BaseCrudViewSet):
    """应用系统。"""

    service = AppSystemService
    serializer_class = AppSystemListSerializer
    write_serializer_class = AppSystemWriteSerializer
    created_message = "应用系统创建成功"
    updated_message = "应用系统更新成功"
    deleted_message = "应用系统已删除"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AppSystemSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return self.service.list_app_systems(
            domain_id=self.request.query_params.get("domain_id"),
            tier=self.request.query_params.get("tier"),
            status=self.request.query_params.get("status"),
            keyword=self.request.query_params.get("keyword"),
        )


class ApplicationViewSet(BaseCrudViewSet):
    """应用。"""

    service = ApplicationService
    serializer_class = ApplicationListSerializer
    write_serializer_class = ApplicationWriteSerializer
    created_message = "应用创建成功"
    updated_message = "应用更新成功"
    deleted_message = "应用已删除"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ApplicationSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return self.service.list_applications(
            app_system_id=self.request.query_params.get("app_system_id"),
            app_kind=self.request.query_params.get("app_kind"),
            status=self.request.query_params.get("status"),
            keyword=self.request.query_params.get("keyword"),
        )


class AppComponentViewSet(BaseCrudViewSet):
    """应用组件（app / database / middleware 统一入口，按 component_type 过滤）。"""

    service = AppComponentService
    serializer_class = AppComponentListSerializer
    write_serializer_class = AppComponentWriteSerializer
    created_message = "应用组件创建成功"
    updated_message = "应用组件更新成功"
    deleted_message = "应用组件已删除"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AppComponentSerializer
        return super().get_serializer_class()

    def service_create(self, payload, user):
        return self.service.create_component(payload)

    def service_update(self, pk, payload):
        return self.service.update_component(pk, payload)

    def get_queryset(self):
        return self.service.list_components(
            application_id=self.request.query_params.get("application_id"),
            component_type=self.request.query_params.get("component_type"),
            db_kind=self.request.query_params.get("db_kind"),
            middleware_kind=self.request.query_params.get("middleware_kind"),
            status=self.request.query_params.get("status"),
            keyword=self.request.query_params.get("keyword"),
        )

    @action(detail=False, methods=["get"])
    def database(self, request):
        """仅数据库组件：/cmdb/components/database/。"""
        return self._typed_list(AppComponentService.model.ComponentType.DATABASE)

    @action(detail=False, methods=["get"])
    def middleware(self, request):
        """仅中间件组件：/cmdb/components/middleware/。"""
        return self._typed_list(AppComponentService.model.ComponentType.MIDDLEWARE)

    @action(detail=False, methods=["get"])
    def app(self, request):
        """仅业务应用组件：/cmdb/components/app/。"""
        return self._typed_list(AppComponentService.model.ComponentType.APP)

    def _typed_list(self, component_type: str):
        qs = self.filter_queryset(self.get_queryset().filter(component_type=component_type))
        page = self.paginate_queryset(qs)
        data = self.paginator.get_paginated_response(
            self.get_serializer(page, many=True).data,
        ).data
        return responses.success(data)
