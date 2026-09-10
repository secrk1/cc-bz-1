"""views 层：轻量分发 —— 入参初验、调用 Service、包装统一响应信封。"""

from rest_framework import status as http_status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.cicd.serializers import PipelineSerializer, PipelineWriteSerializer
from apps.cicd.services import PipelineService
from core import responses


class PipelineViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = PipelineSerializer

    def get_queryset(self):
        return PipelineService.list_pipelines(
            status=self.request.query_params.get("status"),
            keyword=self.request.query_params.get("keyword"),
        )

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)
        data = self.paginator.get_paginated_response(serializer.data).data
        return responses.success(data)

    def retrieve(self, request, *args, **kwargs):
        pipeline = PipelineService.get_pipeline(kwargs["pk"])
        return responses.success(PipelineSerializer(pipeline).data)

    def create(self, request, *args, **kwargs):
        serializer = PipelineWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pipeline = PipelineService.create_pipeline(serializer.validated_data, request.user)
        return responses.success(
            PipelineSerializer(pipeline).data,
            message="流水线创建成功",
            http_status_code=http_status.HTTP_201_CREATED,
        )
