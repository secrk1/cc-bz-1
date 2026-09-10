<script setup>
import { ref } from 'vue'

import PageHeader from '@/components/PageHeader.vue'
import HostSidebar from './components/HostSidebar.vue'
import TerminalPane from './components/TerminalPane.vue'
import { hosts } from './mock'

const activeHost = ref(hosts[0])

const handleSelect = (host) => {
  activeHost.value = host
}
</script>

<template>
  <div class="flex h-full flex-col space-y-5">
    <PageHeader title="运维终端控制台" description="多环境主机 Web SSH，实时会话审计与命令协同（通道预留）" />

    <div class="flex min-h-0 flex-1 gap-5">
      <HostSidebar @select="handleSelect" />
      <TerminalPane :host="activeHost" />
    </div>
  </div>
</template>
