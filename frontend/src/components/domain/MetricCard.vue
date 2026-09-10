<script setup>
// 领域首页指标卡片：纯展示，数据由各子系统首页通过 DomainHome 注入
defineProps({
  metric: { type: Object, required: true },
})

const toneClass = {
  cyan: 'from-cyan-500/20 to-cyan-500/5 text-cyan-300 border-cyan-500/30',
  indigo: 'from-indigo-500/20 to-indigo-500/5 text-indigo-300 border-indigo-500/30',
  emerald: 'from-emerald-500/20 to-emerald-500/5 text-emerald-300 border-emerald-500/30',
  amber: 'from-amber-500/20 to-amber-500/5 text-amber-300 border-amber-500/30',
  rose: 'from-rose-500/20 to-rose-500/5 text-rose-300 border-rose-500/30',
}
</script>

<template>
  <div
    class="rounded-xl border bg-gradient-to-br p-5 transition-transform hover:-translate-y-0.5"
    :class="toneClass[metric.tone || 'cyan']"
  >
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-slate-400">{{ metric.label }}</p>
        <p class="mt-2 text-3xl font-semibold text-slate-100">
          {{ metric.value }}<span
            v-if="metric.suffix"
            class="ml-1 text-sm font-normal text-slate-500"
          >{{ metric.suffix }}</span>
        </p>
      </div>
      <div class="rounded-lg bg-slate-900/60 p-2">
        <el-icon class="text-xl"><component :is="metric.icon" /></el-icon>
      </div>
    </div>
    <p v-if="metric.trend" class="mt-3 text-xs text-slate-500">{{ metric.trend }}</p>
  </div>
</template>
