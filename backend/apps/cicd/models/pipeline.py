"""流水线基础数据模型（占位，后续扩展 Stage / PipelineRun / Artifact）。"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Pipeline(TimeStampedModel):
    class Trigger(models.TextChoices):
        MANUAL = "manual", "手动触发"
        PUSH = "push", "代码推送"
        TAG = "tag", "标签发布"
        SCHEDULE = "schedule", "定时调度"

    class Status(models.TextChoices):
        ACTIVE = "active", "启用"
        DISABLED = "disabled", "停用"

    name = models.CharField("流水线名称", max_length=128)
    code = models.CharField("流水线标识", max_length=64, unique=True)
    repo_url = models.URLField("代码仓库地址", max_length=512)
    default_branch = models.CharField("默认分支", max_length=128, default="main")
    trigger = models.CharField(
        "触发方式", max_length=16, choices=Trigger.choices, default=Trigger.MANUAL,
    )
    status = models.CharField(
        "状态", max_length=16, choices=Status.choices, default=Status.ACTIVE, db_index=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="负责人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_pipelines",
    )
    description = models.CharField("描述", max_length=255, blank=True, default="")

    class Meta:
        db_table = "cicd_pipeline"
        verbose_name = "流水线"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name}({self.code})"
