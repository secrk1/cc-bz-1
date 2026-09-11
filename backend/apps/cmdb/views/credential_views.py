"""
views 层：凭据账号。

安全要点：
- 列表 / 详情默认不返回任何秘密字段；
- reveal 为显式解密动作，单独审计入口（系统账号与登录账号均受控）；
- 口令 / 私钥仅可写入与轮换，不可通过普通读接口获取。
"""

from rest_framework.decorators import action

from apps.cmdb.serializers import (
    CredentialAccountSerializer,
    CredentialAccountWriteSerializer,
    CredentialRevealSerializer,
    CredentialRotateSerializer,
)
from apps.cmdb.services import CredentialService
from core import responses

from core.crud_views import BaseCrudViewSet


class CredentialAccountViewSet(BaseCrudViewSet):
    service = CredentialService
    serializer_class = CredentialAccountSerializer
    write_serializer_class = CredentialAccountWriteSerializer
    created_message = "凭据账号创建成功"
    updated_message = "凭据账号更新成功"
    deleted_message = "凭据账号已删除"

    def get_queryset(self):
        params = self.request.query_params
        return CredentialService.list_credentials(
            server_id=params.get("server_id"),
            account_type=params.get("account_type"),
            protocol=params.get("protocol"),
            is_active=_parse_bool(params.get("is_active")),
            keyword=params.get("keyword"),
        )

    def service_create(self, payload, user):
        return CredentialService.create_credential(payload)

    def service_update(self, pk, payload):
        return CredentialService.update_credential(pk, payload)

    @action(detail=True, methods=["post"])
    def reveal(self, request, pk=None):
        """显式解密返回口令 / 私钥（应仅授予受控角色并留审计）。"""
        credential = CredentialService.get_credential(pk)
        return responses.success(
            CredentialRevealSerializer(credential).data,
            message="凭据明文仅用于本次受控查看",
        )

    @action(detail=True, methods=["post"], url_path="rotate-secret")
    def rotate_secret(self, request, pk=None):
        serializer = CredentialRotateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        credential = CredentialService.rotate_secret(
            pk,
            password=data.get("password"),
            private_key=data.get("private_key"),
            passphrase=data.get("passphrase"),
        )
        return responses.success(
            CredentialAccountSerializer(credential).data, message="凭据已轮换")

    @action(detail=True, methods=["post"])
    def enable(self, request, pk=None):
        return self._toggle_active(pk, True, "凭据已启用")

    @action(detail=True, methods=["post"])
    def disable(self, request, pk=None):
        return self._toggle_active(pk, False, "凭据已停用")

    @action(detail=True, methods=["post"], url_path="verify-result")
    def verify_result(self, request, pk=None):
        """自动化探测回传验证结果（系统账号探测后登记连通性）。"""
        success = bool(request.data.get("success"))
        credential = CredentialService.mark_verify_result(pk, success)
        return responses.success(
            CredentialAccountSerializer(credential).data,
            message="验证结果已登记",
        )

    def _toggle_active(self, pk, is_active: bool, message: str):
        credential = CredentialService.set_active(pk, is_active)
        return responses.success(
            CredentialAccountSerializer(credential).data, message=message)


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.strip().lower() in ("1", "true", "yes", "y")
