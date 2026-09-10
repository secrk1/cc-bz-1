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
            "cluster_endpoint", "namespace", "description",
            "status", "status_display", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EnvironmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = (
            "name", "code", "env_type", "cluster_endpoint",
            "namespace", "description", "status",
        )

    def validate_code(self, value: str) -> str:
        return value.strip().lower()
