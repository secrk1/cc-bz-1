"""
服务器与组件的关系模型：预分配（规划态绑定）与实例（运行态实体）。

- ServerPreAllocation：上线规划阶段，把某环境中的一台服务器预留给某个
  应用组件，携带端口与资源配额；一台服务器可预留给多个不同组件。
- ComponentInstance：组件真正部署后运行在服务器上的具体进程 / 数据实例，
  必须由一条「已预留」的预分配记录落地创建，两者在同一事务内完成状态翻转。
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel

from .domain import AppComponent
from .environment import Environment
from .server import Server


class ServerPreAllocation(TimeStampedModel):
    class Status(models.TextChoices):
        RESERVED = "reserved", "已预留"
        ALLOCATED = "allocated", "已分配"
        RELEASED = "released", "已释放"

    server = models.ForeignKey(
        Server, verbose_name="服务器",
        on_delete=models.PROTECT, related_name="pre_allocations",
    )
    component = models.ForeignKey(
        AppComponent, verbose_name="应用组件",
        on_delete=models.PROTECT, related_name="pre_allocations",
    )
    environment = models.ForeignKey(
        Environment, verbose_name="所属环境",
        on_delete=models.PROTECT, related_name="pre_allocations",
    )
    status = models.CharField("绑定状态", max_length=16, choices=Status.choices,
                              default=Status.RESERVED, db_index=True)
    planned_port = models.PositiveIntegerField("规划端口", null=True, blank=True)
    cpu_quota = models.DecimalField("CPU 配额(核)", max_digits=5, decimal_places=2,
                                    null=True, blank=True)
    memory_quota_mb = models.PositiveIntegerField("内存配额(MB)", null=True, blank=True)
    disk_quota_gb = models.PositiveIntegerField("磁盘配额(GB)", null=True, blank=True)
    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="分配人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="made_pre_allocations",
    )
    allocated_at = models.DateTimeField("分配时间", null=True, blank=True)
    released_at = models.DateTimeField("释放时间", null=True, blank=True)
    remark = models.CharField("备注", max_length=255, blank=True, default="")

    class Meta:
        db_table = "cmdb_server_preallocation"
        verbose_name = "服务器预分配"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)
        constraints = [
            # 同一环境下同一台服务器与同一组件只允许存在一条生效中的绑定
            models.UniqueConstraint(
                fields=("server", "component", "environment"),
                condition=~models.Q(status="released"),
                name="uniq_active_preallocation",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.server.hostname} -> {self.component.name}[{self.status}]"


class ComponentInstance(TimeStampedModel):
    class Role(models.TextChoices):
        STANDALONE = "standalone", "单机"
        MASTER = "master", "主节点"
        SLAVE = "slave", "从节点"
        REPLICA = "replica", "副本"

    class Status(models.TextChoices):
        PROVISIONING = "provisioning", "部署中"
        RUNNING = "running", "运行中"
        STOPPED = "stopped", "已停止"
        ABNORMAL = "abnormal", "异常"

    pre_allocation = models.ForeignKey(
        ServerPreAllocation, verbose_name="来源预分配",
        on_delete=models.PROTECT, related_name="instances",
    )
    component = models.ForeignKey(
        AppComponent, verbose_name="应用组件",
        on_delete=models.PROTECT, related_name="instances",
    )
    server = models.ForeignKey(
        Server, verbose_name="运行服务器",
        on_delete=models.PROTECT, related_name="instances",
    )
    environment = models.ForeignKey(
        Environment, verbose_name="所属环境",
        on_delete=models.PROTECT, related_name="instances",
    )
    name = models.CharField("实例名称", max_length=128)
    instance_code = models.CharField("实例标识", max_length=64, unique=True)
    role = models.CharField("实例角色", max_length=16, choices=Role.choices,
                            default=Role.STANDALONE)
    status = models.CharField("运行状态", max_length=16, choices=Status.choices,
                              default=Status.PROVISIONING, db_index=True)
    listen_port = models.PositiveIntegerField("监听端口", null=True, blank=True)
    version = models.CharField("运行版本", max_length=64, blank=True, default="")
    base_path = models.CharField("部署路径", max_length=255, blank=True, default="")
    pid = models.PositiveIntegerField("进程号", null=True, blank=True)
    extra = models.JSONField("实例附加信息", default=dict, blank=True)
    started_at = models.DateTimeField("最近启动时间", null=True, blank=True)
    operated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="最近操作人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="operated_instances",
    )

    class Meta:
        db_table = "cmdb_component_instance"
        verbose_name = "组件实例"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)
        constraints = [
            # 同一台服务器上同一端口只能有一个未停止的实例
            models.UniqueConstraint(
                fields=("server", "listen_port"),
                condition=~models.Q(status="stopped"),
                name="uniq_active_server_port",
            ),
        ]
        indexes = [
            models.Index(fields=("environment", "status"), name="idx_instance_env_status"),
            models.Index(fields=("component", "environment"), name="idx_instance_component_env"),
        ]

    def __str__(self) -> str:
        return f"{self.instance_code}@{self.server.hostname}"
