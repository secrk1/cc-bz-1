<script setup>
import { computed, ref } from 'vue'

import { envTagType, hosts } from '../mock'

const keyword = ref('')
const selectedId = ref(hosts[0].id)

const emits = defineEmits(['select'])

const filteredHosts = computed(() =>
  hosts.filter(
    (host) =>
      !keyword.value ||
      host.name.includes(keyword.value) ||
      host.ip.includes(keyword.value),
  ),
)

const statusDot = {
  online: 'bg-emerald-400',
  busy: 'bg-amber-400',
  offline: 'bg-slate-600',
}

const statusText = {
  online: 'text-emerald-300',
  busy: 'text-amber-300',
  offline: 'text-slate-500',
}

const handleSelect = (host) => {
  if (host.status === 'offline') return
  selectedId.value = host.id
  emits('select', host)
}
</script>

<template>
  <aside class="flex w-72 shrink-0 flex-col rounded-xl border border-slate-800 bg-slate-900/50">
    <div class="border-b border-slate-800 p-3">
      <el-input v-model="keyword" size="small" placeholder="搜索主机名 / IP" :prefix-icon="'Search'" clearable />
    </div>

    <el-scrollbar class="flex-1">
      <ul class="space-y-1 p-2">
        <li v-for="host in filteredHosts" :key="host.id">
          <button
            class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition-colors"
            :class="[
              selectedId === host.id ? 'bg-cyber-500/10 ring-1 ring-cyber-500/40' : 'hover:bg-slate-800/60',
              host.status === 'offline' ? 'cursor-not-allowed opacity-50' : '',
            ]"
            @click="handleSelect(host)"
          >
            <span class="relative flex h-2.5 w-2.5 shrink-0">
              <span
                v-if="host.status === 'online'"
                class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50"
              ></span>
              <span class="relative inline-flex h-2.5 w-2.5 rounded-full" :class="statusDot[host.status]"></span>
            </span>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-slate-200">{{ host.name }}</p>
              <p class="truncate font-mono text-[11px] text-slate-500">{{ host.ip }}</p>
            </div>
            <el-tag :type="envTagType[host.env]" size="small" effect="dark">{{ host.env }}</el-tag>
          </button>
        </li>
      </ul>
    </el-scrollbar>

    <footer class="border-t border-slate-800 px-4 py-2.5 text-[11px]" :class="statusText[Object.values(hosts).find((h) => h.id === selectedId)?.status || 'online']">
      在线 {{ hosts.filter((h) => h.status !== 'offline').length }} / {{ hosts.length }} 台主机
    </footer>
  </aside>
</template>
