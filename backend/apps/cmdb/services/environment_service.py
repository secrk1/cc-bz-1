"""
Service 层：运行环境核心业务逻辑。

事务编排、唯一性冲突转换、状态机控制均收敛于此；
View 与 Model 都不得承载这些逻辑。
"""

from django.db import transaction
from django.db.utils import IntegrityError

from apps.cmdb.models import Environment
from core.exceptions import BizException, NotFoundError


class EnvironmentService:
    @staticmethod
    def list_environments(*, env_type: str | None = None,
                          status: str | None = None,
                          keyword: str | None = None):
        qs = Environment.objects.all()
        if env_type:
            qs = qs.filter(env_type=env_type)
        if status:
            qs = qs.filter(status=status)
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        return qs.order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def create_environment(payload: dict, created_by=None) -> Environment:
        try:
            return Environment.objects.create(created_by=created_by, **payload)
        except IntegrityError as exc:
            raise BizException("环境标识已存在", code=4090) from exc

    @staticmethod
    def get_environment(pk: int) -> Environment:
        env = Environment.objects.filter(pk=pk).first()
        if env is None:
            raise NotFoundError("运行环境不存在")
        return env

    @staticmethod
    @transaction.atomic
    def update_environment(pk: int, payload: dict) -> Environment:
        env = EnvironmentService.get_environment(pk)
        for field, value in payload.items():
            setattr(env, field, value)
        try:
            env.save()
        except IntegrityError as exc:
            raise BizException("环境标识已存在", code=4090) from exc
        return env

    @staticmethod
    @transaction.atomic
    def change_status(pk: int, target_status: str) -> Environment:
        """状态机：active <-> inactive/maintaining，禁止从不存在的状态跳转。"""
        allowed = dict(Environment.Status.choices)
        if target_status not in allowed:
            raise BizException(f"非法目标状态: {target_status}")
        env = EnvironmentService.get_environment(pk)
        env.status = target_status
        env.save(update_fields=["status", "updated_at"])
        return env

    @staticmethod
    @transaction.atomic
    def delete_environment(pk: int) -> None:
        env = EnvironmentService.get_environment(pk)
        env.delete()
