"""
serializers 层：凭据账号。

安全约束：
- 默认输出序列化器不包含任何秘密字段（口令/私钥/私钥口令），
  数据库中的密文永不通过列表 / 详情接口外泄；
- 仅 ``CredentialRevealSerializer`` 配合显式 reveal 动作解密返回；
- 写序列化器的秘密字段为 write_only，入参明文经模型字段透明加密落库。
"""

from rest_framework import serializers

from apps.cmdb.models import CredentialAccount

_SECRET_FIELDS = ("password", "private_key", "passphrase")


class CredentialAccountSerializer(serializers.ModelSerializer):
    """默认视图：不含秘密明文。"""

    account_type_display = serializers.CharField(source="get_account_type_display", read_only=True)
    protocol_display = serializers.CharField(source="get_protocol_display", read_only=True)
    auth_method_display = serializers.CharField(source="get_auth_method_display", read_only=True)
    server_hostname = serializers.CharField(source="server.hostname", read_only=True)
    server_ip = serializers.CharField(source="server.ip_address", read_only=True)
    environment_code = serializers.CharField(source="server.environment.code", read_only=True)
    effective_port = serializers.SerializerMethodField()
    has_password = serializers.SerializerMethodField()
    has_private_key = serializers.SerializerMethodField()

    class Meta:
        model = CredentialAccount
        fields = (
            "id", "server", "server_hostname", "server_ip", "environment_code",
            "name", "account_type", "account_type_display",
            "protocol", "protocol_display",
            "username", "auth_method", "auth_method_display",
            "port", "effective_port",
            "service_name", "default_db", "connect_options",
            "is_active", "last_verified_at", "last_verify_result",
            "has_password", "has_private_key",
            "remark", "created_at", "updated_at",
        )
        read_only_fields = ("id", "last_verified_at", "last_verify_result",
                            "created_at", "updated_at")

    def get_effective_port(self, obj) -> int | None:
        return obj.effective_port()

    def get_has_password(self, obj) -> bool:
        return bool(obj.password)

    def get_has_private_key(self, obj) -> bool:
        return bool(obj.private_key)


class CredentialRevealSerializer(CredentialAccountSerializer):
    """显式 reveal 动作使用：解密返回秘密明文。"""

    class Meta(CredentialAccountSerializer.Meta):
        fields = CredentialAccountSerializer.Meta.fields + _SECRET_FIELDS
        extra_kwargs = {
            "password": {"read_only": True},
            "private_key": {"read_only": True},
            "passphrase": {"read_only": True},
        }


class CredentialAccountWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True,
                                     allow_null=True, style={"input_type": "password"})
    private_key = serializers.CharField(write_only=True, required=False, allow_blank=True,
                                        allow_null=True)
    passphrase = serializers.CharField(write_only=True, required=False, allow_blank=True,
                                       allow_null=True, style={"input_type": "password"})

    class Meta:
        model = CredentialAccount
        fields = (
            "server", "name", "account_type", "protocol",
            "username", "auth_method", "port",
            "password", "private_key", "passphrase",
            "service_name", "default_db", "connect_options",
            "is_active", "remark",
        )

    def validate(self, attrs):
        account_type = attrs.get("account_type")
        if account_type and account_type not in dict(CredentialAccount.AccountType.choices):
            raise serializers.ValidationError({"account_type": "非法账号类型"})
        return attrs


class CredentialRotateSerializer(serializers.Serializer):
    """凭据轮换：全部可选，仅更新传入的秘密字段。"""

    password = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    private_key = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    passphrase = serializers.CharField(required=False, allow_blank=True, allow_null=True)
