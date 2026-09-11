"""serializers 层：应用领域四层（系统域 / 应用系统 / 应用 / 组件）。"""

from rest_framework import serializers

from apps.cmdb.models import AppComponent, Application, AppSystem, SystemDomain


# ---------------------------------------------------------------------------
# 系统域
# ---------------------------------------------------------------------------
class SystemDomainSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    owner_name = serializers.StringRelatedField(source="owner", read_only=True)
    app_systems_count = serializers.SerializerMethodField()

    class Meta:
        model = SystemDomain
        fields = (
            "id", "name", "code", "owner", "owner_name",
            "description", "status", "status_display",
            "app_systems_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_app_systems_count(self, obj) -> int:
        return obj.app_systems.count()


class SystemDomainWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemDomain
        fields = ("name", "code", "owner", "description", "status")


# ---------------------------------------------------------------------------
# 应用系统
# ---------------------------------------------------------------------------
class AppSystemListSerializer(serializers.ModelSerializer):
    """列表场景：附带系统域概要与子应用统计。"""

    tier_display = serializers.CharField(source="get_tier_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    domain_name = serializers.CharField(source="domain.name", read_only=True)
    domain_code = serializers.CharField(source="domain.code", read_only=True)
    owner_name = serializers.StringRelatedField(source="owner", read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = AppSystem
        fields = (
            "id", "domain", "domain_name", "domain_code",
            "name", "code", "tier", "tier_display",
            "owner", "owner_name", "description", "status", "status_display",
            "applications_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_applications_count(self, obj) -> int:
        return obj.applications.count()


class AppSystemSerializer(AppSystemListSerializer):
    """详情场景：内嵌完整系统域信息。"""

    domain_detail = SystemDomainSerializer(source="domain", read_only=True)

    class Meta(AppSystemListSerializer.Meta):
        fields = AppSystemListSerializer.Meta.fields + ("domain_detail",)


class AppSystemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSystem
        fields = ("domain", "name", "code", "tier", "owner", "description", "status")


# ---------------------------------------------------------------------------
# 应用
# ---------------------------------------------------------------------------
class ApplicationListSerializer(serializers.ModelSerializer):
    app_kind_display = serializers.CharField(source="get_app_kind_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    app_system_name = serializers.CharField(source="app_system.name", read_only=True)
    app_system_code = serializers.CharField(source="app_system.code", read_only=True)
    domain_name = serializers.CharField(source="app_system.domain.name", read_only=True)
    owner_name = serializers.StringRelatedField(source="owner", read_only=True)
    component_counts = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            "id", "app_system", "app_system_name", "app_system_code", "domain_name",
            "name", "code", "app_kind", "app_kind_display",
            "language", "framework",
            "owner", "owner_name",
            "description", "status", "status_display",
            "component_counts", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_component_counts(self, obj) -> dict:
        return {
            "total": obj.components.count(),
            "app": obj.components.filter(component_type=AppComponent.ComponentType.APP).count(),
            "database": obj.components.filter(
                component_type=AppComponent.ComponentType.DATABASE).count(),
            "middleware": obj.components.filter(
                component_type=AppComponent.ComponentType.MIDDLEWARE).count(),
        }


class ApplicationSerializer(ApplicationListSerializer):
    """详情：内嵌应用系统（含系统域）。"""

    app_system_detail = AppSystemListSerializer(source="app_system", read_only=True)

    class Meta(ApplicationListSerializer.Meta):
        fields = ApplicationListSerializer.Meta.fields + ("app_system_detail",)


class ApplicationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = (
            "app_system", "name", "code", "app_kind",
            "language", "framework", "owner", "description", "status",
        )


# ---------------------------------------------------------------------------
# 应用组件（app / database / middleware）
# ---------------------------------------------------------------------------
class AppComponentListSerializer(serializers.ModelSerializer):
    component_type_display = serializers.CharField(
        source="get_component_type_display", read_only=True)
    kind = serializers.CharField(source="kind_display", read_only=True)
    application_code = serializers.CharField(source="application.code", read_only=True)
    application_name = serializers.CharField(source="application.name", read_only=True)
    app_system_name = serializers.CharField(
        source="application.app_system.name", read_only=True)
    active_allocations_count = serializers.SerializerMethodField()
    active_instances_count = serializers.SerializerMethodField()

    class Meta:
        model = AppComponent
        fields = (
            "id", "application", "application_code", "application_name", "app_system_name",
            "name", "code", "component_type", "component_type_display", "kind",
            "runtime_kind", "db_kind", "middleware_kind",
            "version", "default_port", "config", "status",
            "active_allocations_count", "active_instances_count",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_active_allocations_count(self, obj) -> int:
        return obj.pre_allocations.exclude(status="released").count()

    def get_active_instances_count(self, obj) -> int:
        return obj.instances.exclude(status="stopped").count()


class AppComponentSerializer(AppComponentListSerializer):
    application_detail = ApplicationListSerializer(source="application", read_only=True)

    class Meta(AppComponentListSerializer.Meta):
        fields = AppComponentListSerializer.Meta.fields + ("application_detail",)


class AppComponentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppComponent
        fields = (
            "application", "name", "code", "component_type",
            "runtime_kind", "db_kind", "middleware_kind",
            "version", "default_port", "config", "status",
        )

    def validate(self, attrs):
        component_type = attrs.get("component_type")
        db_kind = attrs.get("db_kind") or ""
        middleware_kind = attrs.get("middleware_kind") or ""
        if component_type == AppComponent.ComponentType.DATABASE and not db_kind:
            raise serializers.ValidationError({"db_kind": "数据库组件必须指定数据库类型"})
        if component_type == AppComponent.ComponentType.MIDDLEWARE and not middleware_kind:
            raise serializers.ValidationError(
                {"middleware_kind": "中间件组件必须指定中间件类型"})
        return attrs
