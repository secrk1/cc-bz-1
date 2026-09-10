<script setup>
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const tagClass = {
  dev: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
  staging: 'border-amber-500/40 bg-amber-500/10 text-amber-300',
  prod: 'border-rose-500/40 bg-rose-500/10 text-rose-300',
}
</script>

<template>
  <el-dropdown trigger="click" @command="appStore.setCurrentEnv($event)">
    <button
      class="flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm transition-colors hover:border-cyber-500/60"
      :class="tagClass[appStore.currentEnv]"
    >
      <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-current"></span>
      {{ appStore.currentEnvMeta.label }}
      <el-icon class="text-xs"><ArrowDown /></el-icon>
    </button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="env in appStore.environments"
          :key="env.value"
          :command="env.value"
          :class="env.value === appStore.currentEnv ? 'text-cyber-400' : ''"
        >
          <div class="flex items-center gap-2">
            <el-tag :type="env.tagType" size="small" effect="dark">{{ env.value }}</el-tag>
            <span>{{ env.label }}</span>
          </div>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>
