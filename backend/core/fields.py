"""
自定义模型字段：敏感数据密文落库。

``EncryptedTextField`` 对写入 PostgreSQL 的值自动加密、读出时解密；
数据库中永远是密文，ORM 取到的是明文。禁止对该字段做等值/模糊查询
（同一明文每次密文均不同），只能由其它索引列定位记录后解密使用。
"""

from django.db import models

from . import crypto


class EncryptedTextField(models.TextField):
    description = "应用层透明加密文本字段（密文落库）"

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        return crypto.encrypt(str(value))

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return crypto.decrypt(value)

    def to_python(self, value):
        # 表单/序列化器入口拿到的是明文，无需解密
        return value
