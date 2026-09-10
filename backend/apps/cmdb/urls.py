"""配置中心 REST 路由，统一收口在 /api/v1/cmdb/ 前缀下。"""

from rest_framework.routers import DefaultRouter

from apps.cmdb.views import EnvironmentViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"environments", EnvironmentViewSet, basename="environment")

urlpatterns = router.urls
