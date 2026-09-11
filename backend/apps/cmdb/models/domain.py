"""
CMDB 应用领域四层模型：系统域 -> 应用系统 -> 应用 -> 应用组件。

组件层通过 ``component_type`` 鉴别字段统一承载：
- app        应用组件（业务进程 / 服务）
- database   数据库组件（MySQL / Oracle / ...）
- middleware 中间件组件（Redis / Kafka / ...）

具体形态字段（db_kind / middleware_kind / runtime_kind）按类型填写，
config 保存组件级补充配置；模型层只做数据约束，不含业务编排。
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class SystemDomain(TimeStampedModel):
    """系统域：企业 IT 顶层业务域（如：交易域、数据域、办公域）。"""

    class Status(models.TextChoices):
        ACTIVE = "active", "在用"
        INACTIVE = "inactive", "停用"

    name = models.CharField("系统域名称", max_length=128, unique=True)
    code = models.CharField("系统域标识", max_length=64, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="负责人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_domains",
    )
    description = models.CharField("描述", max_length=255, blank=True, default="")
    status = models.CharField("状态", max_length=16, choices=Status.choices,
                              default=Status.ACTIVE, db_index=True)

    class Meta:
        db_table = "cmdb_system_domain"
        verbose_name = "系统域"
        verbose_name_plural = verbose_name
        ordering = ("code",)

    def __str__(self) -> str:
        return f"{self.name}({self.code})"


class AppSystem(TimeStampedModel):
    """应用系统：系统域下的一套独立业务系统（如：订单系统）。"""

    class Tier(models.TextChoices):
        CORE = "core", "核心系统"
        IMPORTANT = "important", "重要系统"
        NORMAL = "normal", "一般系统"

    class Status(models.TextChoices):
        ACTIVE = "active", "在用"
        INACTIVE = "inactive", "停用"
        PLANNING = "planning", "规划中"

    domain = models.ForeignKey(
        SystemDomain, verbose_name="所属系统域",
        on_delete=models.PROTECT, related_name="app_systems",
    )
    name = models.CharField("应用系统名称", max_length=128)
    code = models.CharField("应用系统标识", max_length=64, unique=True)
    tier = models.CharField("系统等级", max_length=16, choices=Tier.choices,
                            default=Tier.NORMAL, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="负责人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_app_systems",
    )
    description = models.CharField("描述", max_length=255, blank=True, default="")
    status = models.CharField("状态", max_length=16, choices=Status.choices,
                              default=Status.ACTIVE, db_index=True)

    class Meta:
        db_table = "cmdb_app_system"
        verbose_name = "应用系统"
        verbose_name_plural = verbose_name
        ordering = ("code",)
        constraints = [
            models.UniqueConstraint(fields=("domain", "name"), name="uniq_appsystem_domain_name"),
        ]

    def __str__(self) -> str:
        return f"{self.name}({self.code})"


class Application(TimeStampedModel):
    """应用：应用系统内部可独立部署交付的应用（如：订单服务、订单批处理）。"""

    class AppKind(models.TextChoices):
        WEB = "web", "Web 应用"
        SERVICE = "service", "微服务"
        BATCH = "batch", "批处理"
        FRONTEND = "frontend", "前端应用"
        GATEWAY = "gateway", "网关"
        OTHER = "other", "其他"

    class Status(models.TextChoices):
        ACTIVE = "active", "在用"
        INACTIVE = "inactive", "停用"
        PLANNING = "planning", "规划中"

    app_system = models.ForeignKey(
        AppSystem, verbose_name="所属应用系统",
        on_delete=models.PROTECT, related_name="applications",
    )
    name = models.CharField("应用名称", max_length=128)
    code = models.CharField("应用标识", max_length=64, unique=True)
    app_kind = models.CharField("应用类型", max_length=16, choices=AppKind.choices,
                                default=AppKind.SERVICE, db_index=True)
    language = models.CharField("开发语言", max_length=32, blank=True, default="")
    framework = models.CharField("技术框架", max_length=64, blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="负责人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_applications",
    )
    description = models.CharField("描述", max_length=255, blank=True, default="")
    status = models.CharField("状态", max_length=16, choices=Status.choices,
                              default=Status.ACTIVE, db_index=True)

    class Meta:
        db_table = "cmdb_application"
        verbose_name = "应用"
        verbose_name_plural = verbose_name
        ordering = ("code",)
        constraints = [
            models.UniqueConstraint(fields=("app_system", "name"), name="uniq_application_system_name"),
        ]

    def __str__(self) -> str:
        return f"{self.name}({self.code})"


class AppComponent(TimeStampedModel):
    """
    应用组件：应用下最细粒度的可部署 / 可纳管单元。

    三个子类型共用一张表，以 component_type 区分：
    业务应用组件（app）、数据库组件（database）、中间件组件（middleware）。
    """

    class ComponentType(models.TextChoices):
        APP = "app", "应用组件"
        DATABASE = "database", "数据库组件"
        MIDDLEWARE = "middleware", "中间件组件"

    class DatabaseKind(models.TextChoices):
        MYSQL = "mysql", "MySQL"
        ORACLE = "oracle", "Oracle"
        POSTGRESQL = "postgresql", "PostgreSQL"
        DB2 = "db2", "DB2"
        OTHER = "other", "其他数据库"

    class MiddlewareKind(models.TextChoices):
        REDIS = "redis", "Redis"
        KAFKA = "kafka", "Kafka"
        RABBITMQ = "rabbitmq", "RabbitMQ"
        NGINX = "nginx", "Nginx"
        NACOS = "nacos", "Nacos"
        ELASTICSEARCH = "elasticsearch", "Elasticsearch"
        OTHER = "other", "其他中间件"

    class RuntimeKind(models.TextChoices):
        JAVA = "java", "Java"
        NODE = "node", "Node.js"
        PYTHON = "python", "Python"
        GO = "go", "Go"
        CPP = "cpp", "C/C++"
        OTHER = "other", "其他运行时"

    class Status(models.TextChoices):
        ACTIVE = "active", "在用"
        INACTIVE = "inactive", "停用"
        DEPRECATED = "deprecated", "已废弃"

    application = models.ForeignKey(
        Application, verbose_name="所属应用",
        on_delete=models.PROTECT, related_name="components",
    )
    name = models.CharField("组件名称", max_length=128)
    code = models.CharField("组件标识", max_length=64)
    component_type = models.CharField(
        "组件类型", max_length=16, choices=ComponentType.choices, db_index=True,
    )
    # 形态描述：按组件类型选择填写
    runtime_kind = models.CharField(
        "运行时类型", max_length=16, choices=RuntimeKind.choices,
        blank=True, default="",
    )
    db_kind = models.CharField(
        "数据库类型", max_length=16, choices=DatabaseKind.choices,
        blank=True, default="",
    )
    middleware_kind = models.CharField(
        "中间件类型", max_length=16, choices=MiddlewareKind.choices,
        blank=True, default="",
    )
    version = models.CharField("版本", max_length=64, blank=True, default="")
    default_port = models.PositiveIntegerField("默认监听端口", null=True, blank=True)
    config = models.JSONField("扩展配置", default=dict, blank=True)
    status = models.CharField("状态", max_length=16, choices=Status.choices,
                              default=Status.ACTIVE, db_index=True)

    class Meta:
        db_table = "cmdb_app_component"
        verbose_name = "应用组件"
        verbose_name_plural = verbose_name
        ordering = ("application__code", "code")
        constraints = [
            models.UniqueConstraint(
                fields=("application", "code"), name="uniq_component_application_code",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name}({self.code}/{self.component_type})"

    @property
    def kind_display(self) -> str:
        """按组件类型返回具体形态（数据库类型 / 中间件类型 / 运行时）。"""
        if self.component_type == self.ComponentType.DATABASE:
            return self.get_db_kind_display()
        if self.component_type == self.ComponentType.MIDDLEWARE:
            return self.get_middleware_kind_display()
        return self.get_runtime_kind_display()
