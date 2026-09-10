"""
模型基类：仅承载公共字段，禁止在此堆砌业务逻辑。
"""

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    is_deleted = models.BooleanField("逻辑删除", default=False, db_index=True)
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """基类仅提供数据状态落库能力，删除编排逻辑必须在 Service 层完成。"""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
