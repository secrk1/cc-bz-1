<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

defineProps({
  collapsed: { type: Boolean, default: false },
})

const route = useRoute()
// el-menu 开启 router 模式后 index 即路由 path，高亮也按 path 匹配
const activeMenu = computed(() => route.path)

// 导航严格对齐五大领域子系统：首页工作台 + 已落地的功能视图
const menus = [
  {
    index: 'monitor',
    label: '监控中心',
    icon: 'Monitor',
    children: [{ index: '/monitor', label: '监控大盘', icon: 'Odometer' }],
  },
  {
    index: 'cmdb',
    label: '配置中心',
    icon: 'Coin',
    children: [
      { index: '/cmdb', label: '工作台', icon: 'HomeFilled' },
      { index: '/cmdb/environments', label: '运行环境', icon: 'Connection' },
      { index: '/cmdb/servers', label: '服务器资产', icon: 'Cpu' },
    ],
  },
  {
    index: 'ops',
    label: '运维中心',
    icon: 'Setting',
    children: [
      { index: '/ops', label: '工作台', icon: 'HomeFilled' },
      { index: '/ops/terminal', label: '终端控制台', icon: 'Monitor' },
    ],
  },
  {
    index: 'cicd',
    label: '持续交付',
    icon: 'SetUp',
    children: [
      { index: '/cicd', label: '工作台', icon: 'HomeFilled' },
      { index: '/cicd/pipelines', label: '流水线看板', icon: 'DataLine' },
    ],
  },
  {
    index: 'settings',
    label: '系统设置',
    icon: 'Tools',
    children: [{ index: '/settings', label: '系统设置', icon: 'HomeFilled' }],
  },
]

// 初始仅展开当前路由所属的一级分组，其余保持折叠
const resolveOpened = (path) => {
  const group = menus.find((g) =>
    g.children.some((item) => path === item.index || path.startsWith(`${item.index}/`)),
  )
  return group ? [group.index] : []
}
const defaultOpeneds = ref(resolveOpened(route.path))
</script>

<template>
  <aside
    class="side-nav flex h-full shrink-0 flex-col border-r border-slate-800 bg-slate-900/80 backdrop-blur transition-all duration-200"
    :class="collapsed ? 'w-16' : 'w-60'"
  >
    <!-- 品牌区 -->
    <div class="flex h-16 items-center gap-2.5 border-b border-slate-800 px-4">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-cyber-500 font-bold text-white shadow-glow-indigo"
      >
        N
      </div>
      <div v-if="!collapsed" class="min-w-0">
        <p class="truncate text-sm font-semibold tracking-wide text-slate-100">NexusOps</p>
        <p class="truncate text-[11px] text-slate-500">DevOps Platform</p>
      </div>
    </div>

    <!-- 五大子系统导航 -->
    <el-scrollbar class="flex-1">
      <el-menu
        :default-active="activeMenu"
        :default-openeds="defaultOpeneds"
        :collapse="collapsed"
        :collapse-transition="false"
        router
        class="!border-r-0 bg-transparent"
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#22d3ee"
      >
        <el-sub-menu v-for="menu in menus" :key="menu.index" :index="menu.index">
          <template #title>
            <el-icon class="text-base"><component :is="menu.icon" /></el-icon>
            <span class="nav-group-label">{{ menu.label }}</span>
          </template>
          <el-menu-item
            v-for="item in menu.children"
            :key="item.index"
            :index="item.index"
            class="nav-sub-item"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.label }}</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-scrollbar>

    <!-- 底部版本标识 -->
    <div v-if="!collapsed" class="border-t border-slate-800 px-4 py-3">
      <p class="text-[11px] text-slate-600">v0.2.0 · domains</p>
    </div>
  </aside>
</template>

<style scoped>
/* ---- 菜单层级：一级分组 / 二级功能项明确区分（沿用深色 + cyan 主题） ---- */
.side-nav :deep(.el-sub-menu__title) {
  height: 44px;
  margin: 2px 10px;
  border-radius: 8px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #cbd5e1;
}
.side-nav :deep(.el-sub-menu__title:hover) {
  background-color: rgba(30, 41, 59, 0.7);
  color: #e2e8f0;
}
.nav-group-label {
  font-size: 13px;
}

/* 二级菜单容器：缩进 + 竖向导轨，强化与一级的从属关系 */
.side-nav :deep(.el-sub-menu .el-menu) {
  position: relative;
  margin: 0 10px 4px 24px;
  padding-left: 10px;
  background-color: transparent;
  border-left: 1px solid rgba(30, 41, 59, 0.9);
}
.side-nav :deep(.nav-sub-item) {
  height: 38px;
  margin: 1px 0;
  padding-left: 12px !important;
  border-radius: 8px;
  font-size: 13px;
  color: #94a3b8;
}
.side-nav :deep(.nav-sub-item:hover) {
  background-color: rgba(30, 41, 59, 0.6);
  color: #e2e8f0;
}
.side-nav :deep(.nav-sub-item.is-active) {
  color: #22d3ee;
  background-color: rgba(34, 211, 238, 0.1);
  font-weight: 600;
}
.side-nav :deep(.nav-sub-item.is-active::before) {
  content: '';
  position: absolute;
  left: -11px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background-color: #22d3ee;
}
</style>
