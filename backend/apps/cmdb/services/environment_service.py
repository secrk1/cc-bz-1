"""
Service 层：运行环境核心业务逻辑。

事务编排、唯一性冲突转换、状态机控制均收敛于此；
View 与 Model 都不得承载这些逻辑。
五套标准环境（dev/sit/uat/pre/prod）由迁移种子初始化，不允许业务侧删除。
"""

from django.db import transaction

from apps.cmdb.models import Environment
from core.exceptions import BizException

from .base import BaseCrudService


class EnvironmentService(BaseCrudService):
    model = Environment
    not_found_message = "运行环境不存在"
    conflict_message = "环境标识已存在"

    @staticmethod
    def list_environments(*, env_type: str | None = None,
                          status: str | None = None,
                          keyword: str | None = None):
        return EnvironmentService.list(
            env_type=env_type, status=status, keyword=keyword,
        ).order_by("sort_order", "-created_at")

    @staticmethod
    @transaction.atomic
    def create_environment(payload: dict, created_by=None) -> Environment:
        EnvironmentService._validate_standard_code(payload)
        payload.setdefault("sort_order", 99)
        return EnvironmentService.create(
            payload, owner_field="created_by", owner=created_by,
        )

    @staticmethod
    @transaction.atomic
    def update_environment(pk: int, payload: dict) -> Environment:
        env = EnvironmentService.get(pk)
        # 标准环境的 code / env_type 锁定，防止破坏五环境基线
        if env.code in Environment.STANDARD_ENV_CODES:
            payload.pop("code", None)
            payload.pop("env_type", None)
        EnvironmentService._validate_standard_code(payload)
        return EnvironmentService.update(pk, payload)

    @staticmethod
    @transaction.atomic
    def change_status(pk: int, target_status: str) -> Environment:
        """状态机：active <-> inactive/maintaining，禁止跳转到未定义状态。"""
        if target_status not in dict(Environment.Status.choices):
            raise BizException(f"非法目标状态: {target_status}")
        env = EnvironmentService.get(pk)
        env.status = target_status
        env.save(update_fields=["status", "updated_at"])
        return env

    @staticmethod
    @transaction.atomic
    def delete_environment(pk: int) -> None:
        env = EnvironmentService.get(pk)
        if env.code in Environment.STANDARD_ENV_CODES:
            raise BizException("标准环境(dev/sit/uat/pre/prod)不允许删除", code=4090)
        env.delete()

    @staticmethod
    def _validate_standard_code(payload: dict) -> None:
        code = payload.get("code")
        if code is not None:
            code = code.strip().lower()
            payload["code"] = code
            if code in Environment.STANDARD_ENV_CODES:
                # 以标准标识建环境时，env_type 必须与 code 一致
                payload.setdefault("env_type", code)
                if payload.get("env_type") != code:
                    raise BizException(f"标准环境 {code} 的环境类型必须为 {code}")
