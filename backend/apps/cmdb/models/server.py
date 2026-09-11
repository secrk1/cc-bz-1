"""
服务器资产模型：物理机 / 虚机 / 云主机统一纳管。

服务器归属于唯一一个标准环境（dev/sit/uat/pre/prod），
承载组件的「预分配」绑定关系与运行中的组件「实例」（见 allocation.py）。
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel

from .environment import Environment


class Server(TimeStampedModel):
    class Provider(models.TextChoices):
        VM = "vm", "虚拟机"
        PHYSICAL = "physical", "物理机"
        CLOUD = "cloud", "云主机"

    class Status(models.TextChoices):
        RUNNING = "running", "运行中"
        STOPPED = "stopped", "已停机"
        MAINTAINING = "maintaining", "维护中"
        ABNORMAL = "abnormal", "异常"
        RETIRED = "retired", "已下线"

    hostname = models.CharField("主机名", max_length=128, unique=True)
    ip_address = models.GenericIPAddressField("管理 IP", unique=True, db_index=True)
    private_ip = models.GenericIPAddressField("内网 IP", null=True, blank=True)
    os_name = models.CharField("操作系统", max_length=128, blank=True, default="")
    os_version = models.CharField("系统版本", max_length=64, blank=True, default="")
    # ---- 规格 ----
    provider = models.CharField("主机类型", max_length=16, choices=Provider.choices,
                                default=Provider.VM, db_index=True)
    cpu_cores = models.PositiveSmallIntegerField("CPU 核数", default=0)
    memory_mb = models.PositiveIntegerField("内存容量(MB)", default=0)
    disk_gb = models.PositiveIntegerField("系统盘容量(GB)", default=0)
    spec = models.CharField("规格型号", max_length=128, blank=True, default="")
    # ---- 归属与状态 ----
    environment = models.ForeignKey(
        Environment, verbose_name="所属环境",
        on_delete=models.PROTECT, related_name="servers",
    )
    status = models.CharField("运行状态", max_length=16, choices=Status.choices,
                              default=Status.RUNNING, db_index=True)
    region = models.CharField("机房/可用区", max_length=64, blank=True, default="")
    tags = models.JSONField("标签", default=list, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="资产负责人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_servers",
    )
    remark = models.CharField("备注", max_length=255, blank=True, default="")

    class Meta:
        db_table = "cmdb_server"
        verbose_name = "服务器"
        verbose_name_plural = verbose_name
        ordering = ("environment_id", "hostname")
        indexes = [
            models.Index(fields=("environment", "status"), name="idx_server_env_status"),
        ]

    def __str__(self) -> str:
        return f"{self.hostname}({self.ip_address})"
