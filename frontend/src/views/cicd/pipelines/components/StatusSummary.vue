<script setup>
import { statusSummary } from '../mock'

const tone = {
  success: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
  running: 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30',
  failed: 'text-rose-300 bg-rose-500/10 border-rose-500/30',
}
</script>

<template>
  <section class="grid grid-cols-3 gap-4">
    <div
      v-for="item in statusSummary"
      :key="item.key"
      class="flex items-center justify-between rounded-xl border px-5 py-4"
      :class="tone[item.key]"
    >
      <div>
        <p class="text-xs uppercase tracking-wider opacity-80">{{ item.label }}</p>
        <p class="mt-1 text-2xl font-semibold">{{ item.value }}</p>
      </div>
      <el-icon class="text-3xl opacity-80" :class="item.key === 'running' ? 'animate-spin' : ''">
        <component :is="item.icon" />
      </el-icon>
    </div>
  </section>
</template>
