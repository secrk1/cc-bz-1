"""
配置中心 REST 路由，统一收口在 /api/v1/cmdb/ 前缀下。

资源体系（基于应用的真实 CMDB）：
- environments          运行环境（dev/sit/uat/pre/prod 五环境）
- domains               系统域
- app-systems           应用系统
- applications          应用
- components            应用组件（app/database/middleware，含类型子路由）
- servers               服务器资产（规格/IP/环境/状态）
- pre-allocations       服务器预分配到组件的绑定关系
- instances             运行在服务器上的组件实例
- credentials           挂载于服务器的凭据账号（系统探测/运维登录）
"""

from rest_framework.routers import DefaultRouter

from apps.cmdb.views import (
    AppComponentViewSet,
    ApplicationViewSet,
    AppSystemViewSet,
    ComponentInstanceViewSet,
    CredentialAccountViewSet,
    EnvironmentViewSet,
    PreAllocationViewSet,
    ServerViewSet,
    SystemDomainViewSet,
)

router = DefaultRouter(trailing_slash=False)

# 多环境
router.register(r"environments", EnvironmentViewSet, basename="environment")
# 应用领域四层
router.register(r"domains", SystemDomainViewSet, basename="domain")
router.register(r"app-systems", AppSystemViewSet, basename="app-system")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"components", AppComponentViewSet, basename="component")
# 服务器资产
router.register(r"servers", ServerViewSet, basename="server")
# 预分配绑定与运行实例
router.register(r"pre-allocations", PreAllocationViewSet, basename="pre-allocation")
router.register(r"instances", ComponentInstanceViewSet, basename="instance")
# 凭据账号
router.register(r"credentials", CredentialAccountViewSet, basename="credential")

urlpatterns = router.urls
