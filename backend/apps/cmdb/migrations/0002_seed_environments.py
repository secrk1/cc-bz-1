"""种子数据：初始化 dev / sit / uat / pre / prod 五套标准环境。"""

from django.db import migrations

STANDARD_ENVIRONMENTS = [
    # code, name, sort_order, description
    ("dev", "开发环境", 10, "研发自测环境"),
    ("sit", "系统集成测试环境", 20, "系统集成测试 / 联调环境"),
    ("uat", "用户验收测试环境", 30, "业务方验收测试环境"),
    ("pre", "预发布环境", 40, "与生产同构的灰度预发布环境"),
    ("prod", "生产环境", 50, "正式生产环境"),
]


def seed_environments(apps, schema_editor):
    Environment = apps.get_model("cmdb", "Environment")
    for code, name, sort_order, description in STANDARD_ENVIRONMENTS:
        Environment.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "env_type": code,
                "sort_order": sort_order,
                "description": description,
                "status": "active",
                "namespace": "default",
            },
        )


def remove_environments(apps, schema_editor):
    Environment = apps.get_model("cmdb", "Environment")
    Environment.objects.filter(code__in=[row[0] for row in STANDARD_ENVIRONMENTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cmdb", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_environments, remove_environments),
    ]
