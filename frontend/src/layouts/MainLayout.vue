<script setup>
import SideNav from './components/SideNav.vue'
import TopBar from './components/TopBar.vue'

import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
</script>

<template>
  <div class="flex h-full w-full overflow-hidden bg-slate-950">
    <!-- 左侧可折叠导航栏 -->
    <SideNav :collapsed="appStore.sidebarCollapsed" />

    <!-- 右侧工作区：顶部工作台 + 主内容 -->
    <div class="flex min-w-0 flex-1 flex-col">
      <TopBar />
      <main class="flex-1 overflow-y-auto bg-slate-950 p-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
