"""serializers 层：服务器预分配与组件实例。"""

from decimal import Decimal

from rest_framework import serializers

from apps.cmdb.models import ComponentInstance, ServerPreAllocation


# ---------------------------------------------------------------------------
# 预分配
# ---------------------------------------------------------------------------
class PreAllocationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    server_hostname = serializers.CharField(source="server.hostname", read_only=True)
    server_ip = serializers.CharField(source="server.ip_address", read_only=True)
    environment_code = serializers.CharField(source="environment.code", read_only=True)
    component_name = serializers.CharField(source="component.name", read_only=True)
    component_code = serializers.CharField(source="component.code", read_only=True)
    component_type = serializers.CharField(source="component.component_type", read_only=True)
    allocated_by_name = serializers.StringRelatedField(source="allocated_by", read_only=True)

    class Meta:
        model = ServerPreAllocation
        fields = (
            "id", "server", "server_hostname", "server_ip",
            "component", "component_name", "component_code", "component_type",
            "environment", "environment_code",
            "status", "status_display",
            "planned_port", "cpu_quota", "memory_quota_mb", "disk_quota_gb",
            "allocated_by", "allocated_by_name",
            "allocated_at", "released_at", "remark",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "status", "allocated_by", "allocated_at", "released_at",
            "created_at", "updated_at",
        )


class PreAllocationCreateSerializer(serializers.Serializer):
    """预分配入参：server_id + component_id + environment_id 三元组。"""

    server_id = serializers.IntegerField(min_value=1)
    component_id = serializers.IntegerField(min_value=1)
    environment_id = serializers.IntegerField(min_value=1)
    planned_port = serializers.IntegerField(min_value=1, max_value=65535, required=False,
                                            allow_null=True)
    cpu_quota = serializers.DecimalField(max_digits=5, decimal_places=2,
                                         min_value=Decimal("0"),
                                         required=False, allow_null=True)
    memory_quota_mb = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    disk_quota_gb = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    remark = serializers.CharField(max_length=255, required=False, allow_blank=True,
                                   default="")


# ---------------------------------------------------------------------------
# 组件实例
# ---------------------------------------------------------------------------
class ComponentInstanceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    server_hostname = serializers.CharField(source="server.hostname", read_only=True)
    server_ip = serializers.CharField(source="server.ip_address", read_only=True)
    environment_code = serializers.CharField(source="environment.code", read_only=True)
    component_name = serializers.CharField(source="component.name", read_only=True)
    component_code = serializers.CharField(source="component.code", read_only=True)
    operated_by_name = serializers.StringRelatedField(source="operated_by", read_only=True)

    class Meta:
        model = ComponentInstance
        fields = (
            "id", "pre_allocation", "component", "component_name", "component_code",
            "server", "server_hostname", "server_ip",
            "environment", "environment_code",
            "name", "instance_code", "role", "role_display",
            "status", "status_display",
            "listen_port", "version", "base_path", "pid", "extra",
            "operated_by", "operated_by_name",
            "started_at", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "pre_allocation", "component", "server", "environment",
            "status", "operated_by", "started_at", "created_at", "updated_at",
        )


class InstanceCreateSerializer(serializers.Serializer):
    """实例创建入参：必须提供来源预分配。"""

    pre_allocation = serializers.IntegerField(min_value=1)
    instance_code = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=128, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=ComponentInstance.Role.choices, required=False)
    listen_port = serializers.IntegerField(min_value=1, max_value=65535, required=False,
                                           allow_null=True)
    version = serializers.CharField(max_length=64, required=False, allow_blank=True)
    base_path = serializers.CharField(max_length=255, required=False, allow_blank=True)
    extra = serializers.DictField(required=False)

    def validate_instance_code(self, value: str) -> str:
        return value.strip()


class InstanceStatusSerializer(serializers.Serializer):
    target_status = serializers.ChoiceField(choices=ComponentInstance.Status.choices)
    extra = serializers.DictField(required=False)
