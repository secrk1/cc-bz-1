<script setup>
import { alertFeed } from '../mock'

const levelMeta = {
  critical: { label: '严重', dot: 'bg-rose-400', text: 'text-rose-300', tag: 'danger' },
  warning: { label: '警告', dot: 'bg-amber-400', text: 'text-amber-300', tag: 'warning' },
  info: { label: '提示', dot: 'bg-cyan-400', text: 'text-cyan-300', tag: 'info' },
}
</script>

<template>
  <section class="flex h-full flex-col rounded-xl border border-slate-800 bg-slate-900/50">
    <header class="flex items-center justify-between border-b border-slate-800 px-5 py-4">
      <div class="flex items-center gap-2">
        <span class="relative flex h-2.5 w-2.5">
          <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-60"></span>
          <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-rose-500"></span>
        </span>
        <h2 class="text-sm font-semibold text-slate-200">实时告警动态</h2>
      </div>
      <el-button text size="small" class="!text-cyber-400">查看全部</el-button>
    </header>

    <el-scrollbar class="flex-1">
      <ul class="divide-y divide-slate-800/70">
        <li v-for="alert in alertFeed" :key="alert.id" class="flex gap-3 px-5 py-3.5 hover:bg-slate-800/30">
          <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full" :class="levelMeta[alert.level].dot"></span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm text-slate-200">{{ alert.title }}</p>
            <div class="mt-1 flex items-center gap-2 text-xs text-slate-500">
              <el-tag size="small" :type="levelMeta[alert.level].tag" effect="dark" round>
                {{ levelMeta[alert.level].label }}
              </el-tag>
              <span>{{ alert.source }}</span>
              <span>·</span>
              <span>{{ alert.time }}</span>
            </div>
          </div>
        </li>
      </ul>
    </el-scrollbar>
  </section>
</template>
