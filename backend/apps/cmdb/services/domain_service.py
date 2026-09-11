"""
Service 层：应用领域四层（系统域 / 应用系统 / 应用 / 应用组件）业务逻辑。

仅承载跨字段校验与标准 CRUD；组件按 component_type 清理 / 强制形态字段。
"""

from django.db import transaction

from apps.cmdb.models import AppComponent, Application, AppSystem, SystemDomain
from core.exceptions import BizException

from .base import BaseCrudService


class SystemDomainService(BaseCrudService):
    model = SystemDomain
    not_found_message = "系统域不存在"
    conflict_message = "系统域名称或标识已存在"

    @staticmethod
    def list_domains(*, status: str | None = None, keyword: str | None = None):
        return SystemDomainService.list(status=status, keyword=keyword)


class AppSystemService(BaseCrudService):
    model = AppSystem
    not_found_message = "应用系统不存在"
    conflict_message = "应用系统名称或标识已存在"

    @staticmethod
    def list_app_systems(*, domain_id: int | None = None,
                         tier: str | None = None,
                         status: str | None = None,
                         keyword: str | None = None):
        return AppSystemService.list(
            domain_id=domain_id, tier=tier, status=status, keyword=keyword,
        ).select_related("domain")


class ApplicationService(BaseCrudService):
    model = Application
    not_found_message = "应用不存在"
    conflict_message = "应用名称或标识已存在"

    @staticmethod
    def list_applications(*, app_system_id: int | None = None,
                          app_kind: str | None = None,
                          status: str | None = None,
                          keyword: str | None = None):
        return ApplicationService.list(
            app_system_id=app_system_id, app_kind=app_kind,
            status=status, keyword=keyword,
        ).select_related("app_system", "app_system__domain")


class AppComponentService(BaseCrudService):
    model = AppComponent
    not_found_message = "应用组件不存在"
    conflict_message = "同一应用下组件标识已存在"

    @staticmethod
    def list_components(*, application_id: int | None = None,
                        component_type: str | None = None,
                        db_kind: str | None = None,
                        middleware_kind: str | None = None,
                        status: str | None = None,
                        keyword: str | None = None):
        qs = AppComponentService.list(
            application_id=application_id, component_type=component_type,
            db_kind=db_kind, middleware_kind=middleware_kind,
            status=status, keyword=keyword,
        ).select_related(
            "application", "application__app_system", "application__app_system__domain",
        )
        return qs

    @staticmethod
    @transaction.atomic
    def create_component(payload: dict) -> AppComponent:
        AppComponentService._normalize_kind_fields(payload)
        return AppComponentService.create(payload)

    @staticmethod
    @transaction.atomic
    def update_component(pk: int, payload: dict) -> AppComponent:
        component = AppComponentService.get(pk)
        component_type = payload.get("component_type", component.component_type)
        # 以「合并后的完整形态」做规整，避免部分更新时误清字段
        merged = {
            "component_type": component_type,
            "db_kind": payload.get("db_kind", component.db_kind),
            "middleware_kind": payload.get("middleware_kind", component.middleware_kind),
            "runtime_kind": payload.get("runtime_kind", component.runtime_kind),
        }
        AppComponentService._normalize_kind_fields(merged)
        payload.update(merged)
        return AppComponentService.update(pk, payload)

    @staticmethod
    def _normalize_kind_fields(payload: dict) -> None:
        """按组件类型约束形态字段：非本类型的形态字段强制清空，本类型必填项校验。"""
        component_type = payload.get("component_type")
        allowed = dict(AppComponent.ComponentType.choices)
        if component_type not in allowed:
            raise BizException(f"非法组件类型: {component_type}")

        db_kind = payload.get("db_kind") or ""
        middleware_kind = payload.get("middleware_kind") or ""
        runtime_kind = payload.get("runtime_kind") or ""

        if component_type == AppComponent.ComponentType.DATABASE:
            if not db_kind:
                raise BizException("数据库组件必须指定数据库类型(db_kind)")
            if db_kind not in dict(AppComponent.DatabaseKind.choices):
                raise BizException(f"非法数据库类型: {db_kind}")
            payload["db_kind"] = db_kind
            payload["middleware_kind"] = ""
        elif component_type == AppComponent.ComponentType.MIDDLEWARE:
            if not middleware_kind:
                raise BizException("中间件组件必须指定中间件类型(middleware_kind)")
            if middleware_kind not in dict(AppComponent.MiddlewareKind.choices):
                raise BizException(f"非法中间件类型: {middleware_kind}")
            payload["middleware_kind"] = middleware_kind
            payload["db_kind"] = ""
        else:
            if runtime_kind and runtime_kind not in dict(AppComponent.RuntimeKind.choices):
                raise BizException(f"非法运行时类型: {runtime_kind}")
            payload["runtime_kind"] = runtime_kind
            payload["db_kind"] = ""
            payload["middleware_kind"] = ""
