"""持续交付中心 REST 路由，统一收口在 /api/v1/cicd/ 前缀下。"""

from rest_framework.routers import DefaultRouter

from apps.cicd.views import PipelineViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"pipelines", PipelineViewSet, basename="pipeline")

urlpatterns = router.urls
