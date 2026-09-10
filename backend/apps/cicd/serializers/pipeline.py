"""serializers 层：入参校验与响应整形。"""

from rest_framework import serializers

from apps.cicd.models import Pipeline


class PipelineSerializer(serializers.ModelSerializer):
    trigger_display = serializers.CharField(source="get_trigger_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    owner_name = serializers.StringRelatedField(source="owner", read_only=True)

    class Meta:
        model = Pipeline
        fields = (
            "id", "name", "code", "repo_url", "default_branch",
            "trigger", "trigger_display", "status", "status_display",
            "owner_name", "description", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PipelineWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipeline
        fields = (
            "name", "code", "repo_url", "default_branch",
            "trigger", "status", "description",
        )

    def validate_code(self, value: str) -> str:
        return value.strip().lower()
