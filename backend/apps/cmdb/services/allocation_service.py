"""
Service 层：服务器预分配与组件实例的事务编排（CMDB 核心业务）。

两条关键事务边界：

1. ``reserve`` 预分配：把环境内一台服务器绑定给某个组件（规划态）。
   - 服务器、组件、环境必须存在；
   - 服务器所属环境必须与目标环境一致，禁止跨环境占用；
   - 同一 (server, component, environment) 只允许一条生效中绑定
     （DB 层 uniq_active_preallocation 兜底，Service 层先给业务报错）。

2. ``create_instance`` 创建实例：由「已预留」的预分配记录落地为运行实例。
   - select_for_update 锁定预分配行，保证并发下只能落地一次；
   - 预分配状态 reserved -> allocated，与实例插入在同一事务内原子翻转；
   - 实例冗余 server/environment/component 三列，与预分配严格对齐；
   - 服务器端口冲突由 uniq_active_server_port 部分唯一索引兜底。

实例状态机：provisioning -> running -> stopped / abnormal（可恢复 running）。
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.cmdb.models import (
    AppComponent,
    ComponentInstance,
    Environment,
    Server,
    ServerPreAllocation,
)
from core.exceptions import BizException, NotFoundError

from .base import BaseCrudService


class AllocationService:
    # ------------------------------------------------------------------
    # 预分配
    # ------------------------------------------------------------------
    @staticmethod
    def list_allocations(*, server_id: int | None = None,
                         component_id: int | None = None,
                         environment_id: int | None = None,
                         status: str | None = None):
        qs = ServerPreAllocation.objects.all().select_related(
            "server", "component", "environment",
            "component__application", "allocated_by",
        )
        if server_id:
            qs = qs.filter(server_id=server_id)
        if component_id:
            qs = qs.filter(component_id=component_id)
        if environment_id:
            qs = qs.filter(environment_id=environment_id)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def get_allocation(pk: int) -> ServerPreAllocation:
        allocation = (
            ServerPreAllocation.objects
            .select_related("server", "component", "environment")
            .filter(pk=pk).first()
        )
        if allocation is None:
            raise NotFoundError("预分配记录不存在")
        return allocation

    @staticmethod
    @transaction.atomic
    def reserve(payload: dict, *, operator=None) -> ServerPreAllocation:
        """创建预分配绑定（reserved）。payload 传 server_id/component_id/environment_id。"""
        server = Server.objects.select_for_update().filter(
            pk=payload.get("server_id"),
        ).first()
        if server is None:
            raise NotFoundError("服务器不存在")
        component = AppComponent.objects.filter(pk=payload.get("component_id")).first()
        if component is None:
            raise NotFoundError("应用组件不存在")
        environment = Environment.objects.filter(pk=payload.get("environment_id")).first()
        if environment is None:
            raise NotFoundError("运行环境不存在")

        # 环境一致性：服务器只能被其所属环境内的部署占用
        if server.environment_id != environment.id:
            raise BizException(
                f"服务器 {server.hostname} 属于 {server.environment.code} 环境，"
                f"不能预分配到 {environment.code} 环境",
            )
        if server.status == Server.Status.RETIRED:
            raise BizException("已下线服务器不可预分配")

        exists = ServerPreAllocation.objects.filter(
            server=server, component=component, environment=environment,
        ).exclude(status=ServerPreAllocation.Status.RELEASED).exists()
        if exists:
            raise BizException("该服务器对此组件已有生效中的预分配", code=4090)

        try:
            return ServerPreAllocation.objects.create(
                server=server,
                component=component,
                environment=environment,
                status=ServerPreAllocation.Status.RESERVED,
                planned_port=payload.get("planned_port"),
                cpu_quota=payload.get("cpu_quota"),
                memory_quota_mb=payload.get("memory_quota_mb"),
                disk_quota_gb=payload.get("disk_quota_gb"),
                remark=payload.get("remark", ""),
                allocated_by=operator,
            )
        except Exception as exc:  # 部分唯一索引并发冲突
            _raise_integrity(exc, "预分配绑定冲突，该组件已绑定此服务器")

    @staticmethod
    @transaction.atomic
    def release(pk: int) -> ServerPreAllocation:
        """释放预分配：仅 reserved 可释放；已落地实例的须先回收实例。"""
        allocation = ServerPreAllocation.objects.select_for_update().filter(pk=pk).first()
        if allocation is None:
            raise NotFoundError("预分配记录不存在")
        if allocation.status == ServerPreAllocation.Status.RELEASED:
            raise BizException("预分配已释放，无需重复操作")
        if allocation.status == ServerPreAllocation.Status.ALLOCATED:
            active = allocation.instances.exclude(
                status=ComponentInstance.Status.STOPPED,
            ).exists()
            if active:
                raise BizException("该预分配已存在运行实例，请先停止并回收实例后再释放")
        allocation.status = ServerPreAllocation.Status.RELEASED
        allocation.released_at = timezone.now()
        allocation.save(update_fields=["status", "released_at", "updated_at"])
        return allocation

    # ------------------------------------------------------------------
    # 组件实例
    # ------------------------------------------------------------------
    @staticmethod
    def list_instances(*, server_id: int | None = None,
                       component_id: int | None = None,
                       environment_id: int | None = None,
                       status: str | None = None,
                       keyword: str | None = None):
        qs = ComponentInstance.objects.all().select_related(
            "server", "component", "environment", "pre_allocation",
            "component__application", "operated_by",
        )
        if server_id:
            qs = qs.filter(server_id=server_id)
        if component_id:
            qs = qs.filter(component_id=component_id)
        if environment_id:
            qs = qs.filter(environment_id=environment_id)
        if status:
            qs = qs.filter(status=status)
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        return qs.order_by("-created_at")

    @staticmethod
    def get_instance(pk: int) -> ComponentInstance:
        instance = (
            ComponentInstance.objects
            .select_related("server", "component", "environment", "pre_allocation")
            .filter(pk=pk).first()
        )
        if instance is None:
            raise NotFoundError("组件实例不存在")
        return instance

    @staticmethod
    @transaction.atomic
    def create_instance(payload: dict, *, operator=None) -> ComponentInstance:
        """
        由预分配创建运行实例（核心事务）：
        锁定预分配行 -> 校验状态/环境/端口 -> 插入实例 -> 翻转预分配为 allocated。
        """
        allocation_id = payload.get("pre_allocation")
        allocation_id = getattr(allocation_id, "id", allocation_id)
        allocation = (
            ServerPreAllocation.objects
            .select_for_update()
            .select_related("server", "component", "environment")
            .filter(pk=allocation_id).first()
        )
        if allocation is None:
            raise NotFoundError("预分配记录不存在")

        if allocation.status == ServerPreAllocation.Status.ALLOCATED:
            raise BizException("该预分配已创建实例，不能重复落地", code=4090)
        if allocation.status == ServerPreAllocation.Status.RELEASED:
            raise BizException("预分配已释放，不能创建实例")

        server = allocation.server
        if server.status in (Server.Status.STOPPED, Server.Status.RETIRED):
            raise BizException(f"服务器当前状态({server.status})不可部署实例")

        # 端口默认取预分配规划端口；冲突由部分唯一索引最终兜底
        listen_port = payload.get("listen_port") or allocation.planned_port
        if listen_port is not None:
            clash = ComponentInstance.objects.filter(
                server=server, listen_port=listen_port,
            ).exclude(status=ComponentInstance.Status.STOPPED).exists()
            if clash:
                raise BizException(f"服务器 {server.hostname} 端口 {listen_port} 已被占用")

        instance = ComponentInstance(
            pre_allocation=allocation,
            component=allocation.component,
            server=server,
            environment=allocation.environment,
            name=payload.get("name") or allocation.component.name,
            instance_code=payload["instance_code"],
            role=payload.get("role", ComponentInstance.Role.STANDALONE),
            status=ComponentInstance.Status.PROVISIONING,
            listen_port=listen_port,
            version=payload.get("version") or allocation.component.version,
            base_path=payload.get("base_path", ""),
            extra=payload.get("extra", {}),
            operated_by=operator,
        )
        try:
            instance.save()
        except Exception as exc:  # noqa: BLE001
            _raise_integrity(exc, "实例创建冲突：实例标识重复或服务器端口已占用")

        allocation.status = ServerPreAllocation.Status.ALLOCATED
        allocation.allocated_at = timezone.now()
        allocation.allocated_by = operator
        allocation.save(update_fields=["status", "allocated_at", "allocated_by", "updated_at"])
        return instance

    @staticmethod
    @transaction.atomic
    def transition_instance(pk: int, target_status: str, *,
                            operator=None, extra: dict | None = None) -> ComponentInstance:
        """实例状态机：provisioning/running/stopped/abnormal 间的合法跳转。"""
        allowed = set(dict(ComponentInstance.Status.choices))
        if target_status not in allowed:
            raise BizException(f"非法实例状态: {target_status}")

        instance = ComponentInstance.objects.select_for_update().filter(pk=pk).first()
        if instance is None:
            raise NotFoundError("组件实例不存在")

        legal = _INSTANCE_TRANSITIONS.get(instance.status, set())
        if target_status != instance.status and target_status not in legal:
            raise BizException(
                f"不允许的实例状态流转: {instance.status} -> {target_status}",
            )

        instance.status = target_status
        if target_status == ComponentInstance.Status.RUNNING:
            instance.started_at = timezone.now()
        if extra:
            merged = dict(instance.extra or {})
            merged.update(extra)
            instance.extra = merged
        if operator is not None:
            instance.operated_by = operator
        update_fields = ["status", "updated_at", "operated_by"]
        if target_status == ComponentInstance.Status.RUNNING:
            update_fields.append("started_at")
        if extra:
            update_fields.append("extra")
        instance.save(update_fields=update_fields)
        return instance

    @staticmethod
    @transaction.atomic
    def delete_instance(pk: int) -> None:
        instance = ComponentInstance.objects.select_for_update().filter(pk=pk).first()
        if instance is None:
            raise NotFoundError("组件实例不存在")
        if instance.status not in (
            ComponentInstance.Status.STOPPED, ComponentInstance.Status.ABNORMAL,
        ):
            raise BizException("仅停止或异常状态的实例允许删除")
        instance.delete()


# provisioning 只能上线为 running；running 可停止 / 异常；stopped/abnormal 可恢复 running
_INSTANCE_TRANSITIONS = {
    ComponentInstance.Status.PROVISIONING: {
        ComponentInstance.Status.RUNNING,
        ComponentInstance.Status.ABNORMAL,
    },
    ComponentInstance.Status.RUNNING: {
        ComponentInstance.Status.STOPPED,
        ComponentInstance.Status.ABNORMAL,
    },
    ComponentInstance.Status.STOPPED: {
        ComponentInstance.Status.RUNNING,
        ComponentInstance.Status.ABNORMAL,
    },
    ComponentInstance.Status.ABNORMAL: {
        ComponentInstance.Status.RUNNING,
        ComponentInstance.Status.STOPPED,
    },
}


class InstanceService(BaseCrudService):
    """供通用 ViewSet 复用的薄封装，实体逻辑全部代理到 AllocationService。"""

    model = ComponentInstance
    not_found_message = "组件实例不存在"

    @staticmethod
    def list_instances(**filters):
        return AllocationService.list_instances(**filters)

    @staticmethod
    def get_instance(pk: int) -> ComponentInstance:
        return AllocationService.get_instance(pk)


def _raise_integrity(exc: Exception, message: str):
    """DB 约束冲突转业务异常，其余异常原样抛出由全局兜底。"""
    from django.db.utils import IntegrityError

    if isinstance(exc, IntegrityError):
        raise BizException(message, code=4090) from exc
    raise exc
