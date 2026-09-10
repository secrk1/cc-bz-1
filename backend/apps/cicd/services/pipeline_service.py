"""
Service 层：流水线业务逻辑占位。

当前仅提供查询/创建编排；触发执行、阶段编排、状态机流转
（Pending -> Running -> Success/Failed/Canceled）后续在此扩展，
并通过 Celery 异步下发。
"""

from django.db import transaction
from django.db.utils import IntegrityError

from apps.cicd.models import Pipeline
from core.exceptions import BizException, NotFoundError


class PipelineService:
    @staticmethod
    def list_pipelines(*, status: str | None = None, keyword: str | None = None):
        qs = Pipeline.objects.all()
        if status:
            qs = qs.filter(status=status)
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        return qs.order_by("-created_at")

    @staticmethod
    def get_pipeline(pk: int) -> Pipeline:
        pipeline = Pipeline.objects.filter(pk=pk).first()
        if pipeline is None:
            raise NotFoundError("流水线不存在")
        return pipeline

    @staticmethod
    @transaction.atomic
    def create_pipeline(payload: dict, owner=None) -> Pipeline:
        try:
            return Pipeline.objects.create(owner=owner, **payload)
        except IntegrityError as exc:
            raise BizException("流水线标识已存在", code=4090) from exc
