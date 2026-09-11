"""
凭据账号模型：挂载在服务器上的登录 / 探测凭据。

两类用途：
- system 系统账号：专供自动化探测 / Agent 采集 / 批量执行，
  通常为低权限或受控 sudo 账号；
- login  登录账号：日常运维 SSH / 数据库登录使用。

支持协议：SSH、MySQL、Oracle、Redis（均可扩展）。
口令 / 私钥通过 ``EncryptedTextField`` 密文落库，REST 默认不回传密文，
仅在显式 ``reveal`` 动作下、按权限解密返回（见 view 层）。
"""

from django.db import models

from core.fields import EncryptedTextField
from core.models import TimeStampedModel

from .server import Server


class CredentialAccount(TimeStampedModel):
    class AccountType(models.TextChoices):
        SYSTEM = "system", "系统账号(自动化探测)"
        LOGIN = "login", "运维登录账号"

    class Protocol(models.TextChoices):
        SSH = "ssh", "SSH"
        MYSQL = "mysql", "MySQL"
        ORACLE = "oracle", "Oracle"
        REDIS = "redis", "Redis"

    class AuthMethod(models.TextChoices):
        PASSWORD = "password", "口令"
        KEY = "key", "密钥"
        NONE = "none", "免密"

    server = models.ForeignKey(
        Server, verbose_name="所属服务器",
        on_delete=models.CASCADE, related_name="credentials",
    )
    name = models.CharField("凭据名称", max_length=128)
    account_type = models.CharField(
        "账号类型", max_length=16, choices=AccountType.choices, db_index=True,
    )
    protocol = models.CharField(
        "协议类型", max_length=16, choices=Protocol.choices, db_index=True,
    )
    username = models.CharField("登录用户名", max_length=128)
    auth_method = models.CharField(
        "认证方式", max_length=16, choices=AuthMethod.choices, default=AuthMethod.PASSWORD,
    )
    port = models.PositiveIntegerField("端口", null=True, blank=True)
    # 敏感字段：密文存储，禁止序列化器默认输出
    password = EncryptedTextField("口令(密文)", null=True, blank=True)
    private_key = EncryptedTextField("私钥(密文)", null=True, blank=True)
    passphrase = EncryptedTextField("私钥口令(密文)", null=True, blank=True)
    # 数据库 / 缓存类协议的附加属性
    service_name = models.CharField("Oracle 服务名", max_length=128, blank=True, default="")
    default_db = models.CharField("默认库/库号", max_length=64, blank=True, default="")
    connect_options = models.JSONField("连接附加参数", default=dict, blank=True)
    is_active = models.BooleanField("是否启用", default=True, db_index=True)
    last_verified_at = models.DateTimeField("最近验证时间", null=True, blank=True)
    last_verify_result = models.BooleanField("最近验证结果", null=True, blank=True)
    remark = models.CharField("备注", max_length=255, blank=True, default="")

    class Meta:
        db_table = "cmdb_credential_account"
        verbose_name = "凭据账号"
        verbose_name_plural = verbose_name
        ordering = ("server_id", "account_type", "protocol")
        constraints = [
            # 同一服务器下 协议+端口+用户名+类型 唯一，避免重复纳管
            models.UniqueConstraint(
                fields=("server", "account_type", "protocol", "port", "username"),
                name="uniq_credential_server_proto_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.username}@{self.server.hostname}[{self.protocol}/{self.account_type}]"

    @property
    def default_port(self) -> int | None:
        return {
            "ssh": 22,
            "mysql": 3306,
            "oracle": 1521,
            "redis": 6379,
        }.get(self.protocol)

    def effective_port(self) -> int | None:
        return self.port or self.default_port
