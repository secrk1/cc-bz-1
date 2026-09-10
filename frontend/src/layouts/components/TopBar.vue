<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import EnvSwitcher from './EnvSwitcher.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

const breadcrumbs = computed(() => route.meta.breadcrumb || [])

const handleLogout = () => {
  authStore.clear()
  router.push('/login')
}
</script>

<template>
  <header
    class="z-10 flex h-16 shrink-0 items-center justify-between gap-4 border-b border-slate-800 bg-slate-900/60 px-5 backdrop-blur"
  >
    <div class="flex items-center gap-4">
      <el-button
        text
        class="!text-slate-400 hover:!text-cyber-400"
        @click="appStore.toggleSidebar()"
      >
        <el-icon class="text-xl"><Fold v-if="!appStore.sidebarCollapsed" /><Expand v-else /></el-icon>
      </el-button>

      <!-- 面包屑 -->
      <el-breadcrumb separator="/" class="hidden sm:block">
        <el-breadcrumb-item
          v-for="(crumb, index) in breadcrumbs"
          :key="index"
          :class="index === breadcrumbs.length - 1 ? '!text-slate-200' : '!text-slate-500'"
        >
          {{ crumb }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="flex items-center gap-3">
      <!-- 环境快速切换器 -->
      <EnvSwitcher />

      <el-tooltip content="通知" placement="bottom">
        <el-badge :value="3" class="cursor-pointer">
          <el-icon class="text-lg text-slate-400 hover:text-cyber-400"><Bell /></el-icon>
        </el-badge>
      </el-tooltip>

      <el-dropdown trigger="click">
        <div class="flex cursor-pointer items-center gap-2 rounded-full py-1 pl-1 pr-3 hover:bg-slate-800/70">
          <el-avatar :size="30" class="!bg-gradient-to-br !from-brand-500 !to-cyber-500">
            {{ (authStore.username || 'op').slice(0, 2).toUpperCase() }}
          </el-avatar>
          <span class="text-sm text-slate-300">{{ authStore.username || 'operator' }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>个人中心（待接入）</el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>
