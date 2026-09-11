"""
Service 层：凭据账号业务逻辑。

- 敏感字段（口令 / 私钥）由 EncryptedTextField 透明加解密，本层只做协议-认证
  方式的组合校验与验证结果登记；
- 系统账号(system)面向自动化探测，登录账号(login)面向日常运维；
- 删除受服务器保护的凭据时级联由模型 on_delete=CASCADE 处理。
"""

from django.db import transaction
from django.utils import timezone

from apps.cmdb.models import CredentialAccount, Server
from core.exceptions import BizException, NotFoundError

from .base import BaseCrudService

# 协议 -> 默认端口 / 支持的认证方式
_PROTOCOL_DEFAULTS = {
    CredentialAccount.Protocol.SSH: {"port": 22, "auth": ("password", "key", "none")},
    CredentialAccount.Protocol.MYSQL: {"port": 3306, "auth": ("password",)},
    CredentialAccount.Protocol.ORACLE: {"port": 1521, "auth": ("password",)},
    CredentialAccount.Protocol.REDIS: {"port": 6379, "auth": ("password", "none")},
}


class CredentialService(BaseCrudService):
    model = CredentialAccount
    not_found_message = "凭据账号不存在"
    conflict_message = "该服务器下协议/端口/用户名的凭据已存在"

    @staticmethod
    def list_credentials(*, server_id: int | None = None,
                         account_type: str | None = None,
                         protocol: str | None = None,
                         is_active: bool | None = None,
                         keyword: str | None = None):
        qs = CredentialService.list(
            server_id=server_id, account_type=account_type,
            protocol=protocol, is_active=is_active,
            keyword=keyword, keyword_field="username",
        ).select_related("server", "server__environment")
        return qs

    @staticmethod
    def get_credential(pk: int) -> CredentialAccount:
        return CredentialService.get(pk)

    @staticmethod
    @transaction.atomic
    def create_credential(payload: dict) -> CredentialAccount:
        CredentialService._validate(server_ref=payload.get("server"), payload=payload)
        return CredentialService.create(payload)

    @staticmethod
    @transaction.atomic
    def update_credential(pk: int, payload: dict) -> CredentialAccount:
        credential = CredentialService.get(pk)
        server_ref = payload.get("server", credential.server_id)
        merged = {
            "protocol": payload.get("protocol", credential.protocol),
            "auth_method": payload.get("auth_method", credential.auth_method),
            "port": payload.get("port", credential.port),
            "service_name": payload.get("service_name", credential.service_name),
            "password": payload.get("password", credential.password),
            "private_key": payload.get("private_key", credential.private_key),
            "passphrase": payload.get("passphrase", credential.passphrase),
        }
        CredentialService._validate(server_ref=server_ref, payload=merged)
        # 合并后规范化端口再回写
        payload["port"] = merged["port"]
        return CredentialService.update(pk, payload)

    @staticmethod
    @transaction.atomic
    def rotate_secret(pk: int, *, password: str | None = None,
                      private_key: str | None = None,
                      passphrase: str | None = None) -> CredentialAccount:
        """轮换敏感凭据：仅更新显式传入的秘密字段。"""
        credential = CredentialService.get(pk)
        updates = ["updated_at"]
        if password is not None:
            credential.password = password or None
            updates.append("password")
        if private_key is not None:
            credential.private_key = private_key or None
            updates.append("private_key")
        if passphrase is not None:
            credential.passphrase = passphrase or None
            updates.append("passphrase")
        # 认证方式随秘密内容联动
        if credential.private_key:
            credential.auth_method = CredentialAccount.AuthMethod.KEY
        elif credential.password:
            credential.auth_method = CredentialAccount.AuthMethod.PASSWORD
        updates.append("auth_method")
        credential.save(update_fields=updates)
        return credential

    @staticmethod
    @transaction.atomic
    def set_active(pk: int, is_active: bool) -> CredentialAccount:
        credential = CredentialService.get(pk)
        credential.is_active = is_active
        credential.save(update_fields=["is_active", "updated_at"])
        return credential

    @staticmethod
    @transaction.atomic
    def mark_verify_result(pk: int, success: bool) -> CredentialAccount:
        credential = CredentialService.get(pk)
        credential.last_verified_at = timezone.now()
        credential.last_verify_result = success
        credential.save(update_fields=["last_verified_at", "last_verify_result", "updated_at"])
        return credential

    @staticmethod
    def _validate(*, server_ref, payload: dict) -> None:
        server_id = getattr(server_ref, "id", server_ref)
        if not Server.objects.filter(pk=server_id).exists():
            raise NotFoundError("挂载的服务器不存在")

        protocol = payload.get("protocol")
        spec = _PROTOCOL_DEFAULTS.get(protocol)
        if spec is None:
            raise BizException(f"不支持的协议类型: {protocol}")

        auth_method = payload.get("auth_method", CredentialAccount.AuthMethod.PASSWORD)
        if auth_method not in spec["auth"]:
            raise BizException(f"{protocol} 协议不支持认证方式: {auth_method}")

        port = payload.get("port")
        payload["port"] = port or spec["port"]

        # Oracle 建议给出服务名（SID/服务名二选一，落在 connect_options 亦可）
        if protocol == CredentialAccount.Protocol.ORACLE and not payload.get("service_name"):
            payload.setdefault("service_name", "ORCL")

        # 认证方式与秘密内容的一致性
        if auth_method == CredentialAccount.AuthMethod.PASSWORD and not payload.get("password"):
            raise BizException("口令认证必须提供 password")
        if auth_method == CredentialAccount.AuthMethod.KEY:
            if not payload.get("private_key"):
                raise BizException("密钥认证必须提供 private_key")
            if protocol != CredentialAccount.Protocol.SSH:
                raise BizException("私钥认证仅支持 SSH 协议")
