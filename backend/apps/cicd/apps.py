from django.apps import AppConfig


class CicdConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cicd"
    label = "cicd"
    verbose_name = "持续交付"
