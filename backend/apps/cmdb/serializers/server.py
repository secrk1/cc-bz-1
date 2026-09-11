"""serializers 层：服务器资产。"""

from rest_framework import serializers

from apps.cmdb.models import Server


class ServerSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    provider_display = serializers.CharField(source="get_provider_display", read_only=True)
    environment_name = serializers.CharField(source="environment.name", read_only=True)
    environment_code = serializers.CharField(source="environment.code", read_only=True)
    owner_name = serializers.StringRelatedField(source="owner", read_only=True)
    active_allocations_count = serializers.SerializerMethodField()
    active_instances_count = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = (
            "id", "hostname", "ip_address", "private_ip",
            "os_name", "os_version",
            "provider", "provider_display",
            "cpu_cores", "memory_mb", "disk_gb", "spec",
            "environment", "environment_name", "environment_code",
            "region", "tags", "status", "status_display",
            "owner", "owner_name", "remark",
            "active_allocations_count", "active_instances_count",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_active_allocations_count(self, obj) -> int:
        return obj.pre_allocations.exclude(status="released").count()

    def get_active_instances_count(self, obj) -> int:
        return obj.instances.exclude(status="stopped").count()


class ServerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = (
            "hostname", "ip_address", "private_ip",
            "os_name", "os_version",
            "provider", "cpu_cores", "memory_mb", "disk_gb", "spec",
            "environment", "region", "tags", "status",
            "owner", "remark",
        )
