<script setup>
import { computed } from 'vue'

const props = defineProps({
  host: { type: Object, required: true },
})

// 终端占位输出：后续将由 WebSocket(/ws/...) 流式写入 xterm.js
const bootLines = computed(() => [
  `Connecting to ${props.host.name} (${props.host.ip}) ...`,
  `Environment: ${props.host.env.toUpperCase()}  OS: ${props.host.os}`,
  'WebSocket 通道建立后，此处将挂载 xterm.js 终端（后端 Channels 已预留 ws 路由）。',
])

const tabs = ['SSH 会话', '部署日志（占位）']
</script>

<template>
  <section class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-slate-800 bg-[#0b1120]">
    <!-- 终端标签栏 -->
    <div class="flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-3">
      <div class="flex">
        <div
          v-for="(tab, index) in tabs"
          :key="tab"
          class="cursor-pointer border-b-2 px-4 py-2.5 text-xs"
          :class="index === 0 ? 'border-cyber-400 text-cyber-300' : 'border-transparent text-slate-500'"
        >
          {{ tab }}
        </div>
      </div>
      <div class="flex items-center gap-2 text-xs text-slate-500">
        <span class="rounded bg-slate-800 px-2 py-0.5 font-mono">{{ host.name }}</span>
        <el-icon class="text-slate-600"><Setting /></el-icon>
      </div>
    </div>

    <!-- 黑底命令交互区 -->
    <div class="min-h-0 flex-1 overflow-y-auto p-4 font-mono text-[13px] leading-6">
      <p v-for="(line, index) in bootLines" :key="index" class="text-slate-400">
        <span class="mr-2 text-cyber-500">[boot]</span>{{ line }}
      </p>
      <div class="mt-4 flex items-center text-emerald-400">
        <span class="mr-2">{{ host.env === 'prod' ? 'root' : 'ops' }}@{{ host.name }}</span>
        <span class="mr-2 text-slate-500">:</span>
        <span class="mr-2 text-indigo-300">~</span>
        <span class="mr-2 text-slate-500">$</span>
        <span class="inline-block h-4 w-2 animate-pulse bg-emerald-400"></span>
      </div>
    </div>

    <!-- 底部命令输入占位 -->
    <div class="flex items-center gap-2 border-t border-slate-800 bg-slate-900/70 px-3 py-2">
      <el-icon class="text-slate-500"><Promotion /></el-icon>
      <el-input
        model-value=""
        disabled
        placeholder="终端交互即将上线，命令将通过 WebSocket 实时下发至目标主机"
        class="flex-1"
        :input-style="{ background: 'transparent', color: '#a5b4fc' }"
      />
      <el-tag size="small" type="info" effect="dark">预留通道</el-tag>
    </div>
  </section>
</template>
