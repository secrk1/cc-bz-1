"""
Service 层通用基类：收敛只读查询与标准 CRUD 编排。

子类只需声明 model / not_found_message，并可覆写钩子；
涉及多表状态流转的复杂事务（预分配、实例创建）在独立 Service 中实现。
"""

from django.db import transaction
from django.db.utils import IntegrityError

from core.exceptions import BizException, NotFoundError


class BaseCrudService:
    model = None
    not_found_message = "资源不存在"
    conflict_message = "数据唯一性冲突"

    @classmethod
    def queryset(cls):
        return cls.model.objects.all()

    @classmethod
    def get(cls, pk: int):
        obj = cls.queryset().filter(pk=pk).first()
        if obj is None:
            raise NotFoundError(cls.not_found_message)
        return obj

    @classmethod
    def list(cls, *, keyword: str | None = None, keyword_field: str = "name", **filters):
        qs = cls.queryset()
        for field, value in filters.items():
            if value not in (None, ""):
                qs = qs.filter(**{field: value})
        if keyword:
            qs = qs.filter(**{f"{keyword_field}__icontains": keyword})
        return qs

    @classmethod
    @transaction.atomic
    def create(cls, payload: dict, *, owner_field: str | None = None, owner=None):
        if owner_field and owner is not None:
            payload = {**payload, owner_field: owner}
        try:
            return cls.model.objects.create(**payload)
        except IntegrityError as exc:
            raise BizException(cls.conflict_message, code=4090) from exc

    @classmethod
    @transaction.atomic
    def update(cls, pk: int, payload: dict):
        obj = cls.get(pk)
        for field, value in payload.items():
            setattr(obj, field, value)
        try:
            obj.save()
        except IntegrityError as exc:
            raise BizException(cls.conflict_message, code=4090) from exc
        return obj

    @classmethod
    @transaction.atomic
    def delete(cls, pk: int) -> None:
        obj = cls.get(pk)
        try:
            obj.delete()
        except IntegrityError as exc:
            raise BizException("该资源存在关联数据，不允许删除", code=4090) from exc
