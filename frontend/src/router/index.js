import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/monitor',
    children: [
      // ---- 监控中心 ----
      {
        path: 'monitor',
        name: 'monitor-home',
        component: () => import('@/views/monitor/MonitorHomeView.vue'),
        meta: { title: '监控大盘', breadcrumb: ['监控中心', '监控大盘'] },
      },
      // ---- 配置中心 ----
      {
        path: 'cmdb',
        name: 'cmdb-home',
        component: () => import('@/views/cmdb/CmdbHomeView.vue'),
        meta: { title: '配置中心', breadcrumb: ['配置中心', '工作台'] },
      },
      {
        path: 'cmdb/environments',
        name: 'cmdb-environments',
        component: () => import('@/views/cmdb/environments/EnvironmentsView.vue'),
        meta: { title: '运行环境', breadcrumb: ['配置中心', '运行环境管理'] },
      },
      // ---- 运维中心 ----
      {
        path: 'ops',
        name: 'ops-home',
        component: () => import('@/views/ops/OpsHomeView.vue'),
        meta: { title: '运维中心', breadcrumb: ['运维中心', '工作台'] },
      },
      {
        path: 'ops/terminal',
        name: 'ops-terminal',
        component: () => import('@/views/ops/terminal/TerminalView.vue'),
        meta: { title: '终端控制台', breadcrumb: ['运维中心', '终端控制台'] },
      },
      // ---- 持续交付 ----
      {
        path: 'cicd',
        name: 'cicd-home',
        component: () => import('@/views/cicd/CicdHomeView.vue'),
        meta: { title: '持续交付', breadcrumb: ['持续交付', '工作台'] },
      },
      {
        path: 'cicd/pipelines',
        name: 'cicd-pipelines',
        component: () => import('@/views/cicd/pipelines/PipelinesView.vue'),
        meta: { title: '流水线看板', breadcrumb: ['持续交付', '流水线看板'] },
      },
      // ---- 系统设置 ----
      {
        path: 'settings',
        name: 'settings-home',
        component: () => import('@/views/settings/SettingsHomeView.vue'),
        meta: { title: '系统设置', breadcrumb: ['系统设置'] },
      },
    ],
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { public: true, title: '登录' },
  },
  // 旧版路径平滑重定向，保证书签/历史链接不失效
  { path: '/dashboard', redirect: '/monitor' },
  { path: '/pipelines', redirect: '/cicd/pipelines' },
  { path: '/terminal', redirect: '/ops/terminal' },
  { path: '/settings/environments', redirect: '/cmdb/environments' },
  { path: '/:pathMatch(.*)*', redirect: '/monitor' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || ''} · NexusOps`
  // 骨架阶段不强制拦截，对接真实鉴权后可启用：
  // const auth = useAuthStore()
  // if (!to.meta.public && !auth.isAuthenticated) return { name: 'login' }
  return true
})

export default router
