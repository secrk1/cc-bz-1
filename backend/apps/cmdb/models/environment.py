"""运行环境模型：Dev / Staging / Prod 集群连接配置。"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Environment(TimeStampedModel):
    class EnvType(models.TextChoices):
        DEV = "dev", "开发环境"
        STAGING = "staging", "预发环境"
        PROD = "prod", "生产环境"

    class Status(models.TextChoices):
        ACTIVE = "active", "可用"
        INACTIVE = "inactive", "停用"
        MAINTAINING = "maintaining", "维护中"

    name = models.CharField("环境名称", max_length=64)
    code = models.CharField("环境标识", max_length=32, unique=True)
    env_type = models.CharField("环境类型", max_length=16, choices=EnvType.choices, db_index=True)
    cluster_endpoint = models.URLField("集群 API 地址", max_length=512)
    namespace = models.CharField("默认命名空间", max_length=128, default="default")
    description = models.CharField("描述", max_length=255, blank=True, default="")
    status = models.CharField("状态", max_length=16, choices=Status.choices,
                              default=Status.ACTIVE, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="创建人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_environments",
    )

    class Meta:
        db_table = "cmdb_environment"
        verbose_name = "运行环境"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name}({self.code})"
