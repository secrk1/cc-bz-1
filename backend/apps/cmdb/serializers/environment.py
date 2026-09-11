"""
serializers 层：入参校验与响应整形。

不写事务/状态流转；唯一性等数据库级错误由 Service 层转换为业务异常。
"""

from rest_framework import serializers

from apps.cmdb.models import Environment


class EnvironmentSerializer(serializers.ModelSerializer):
    env_type_display = serializers.CharField(source="get_env_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.StringRelatedField(source="created_by", read_only=True)

    class Meta:
        model = Environment
        fields = (
            "id", "name", "code", "env_type", "env_type_display",
            "cluster_endpoint", "namespace", "sort_order", "description",
            "status", "status_display", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EnvironmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = (
            "name", "code", "env_type", "cluster_endpoint",
            "namespace", "sort_order", "description", "status",
        )

    def validate_code(self, value: str) -> str:
        return value.strip().lower()

    def validate(self, attrs):
        code = attrs.get("code")
        env_type = attrs.get("env_type")
        # 标准五环境的 code 与 env_type 必须一致
        if code in Environment.STANDARD_ENV_CODES and env_type and code != env_type:
            raise serializers.ValidationError({"env_type": f"标准环境 {code} 的类型必须为 {code}"})
        return attrs
