<script setup>
import DomainHome from '@/components/domain/DomainHome.vue'

const metrics = [
  { label: '在线会话', value: 3, suffix: '个', trend: '峰值 12 个', icon: 'Monitor', tone: 'cyan' },
  { label: '在线主机', value: 6, suffix: '/ 7 台', trend: '1 台离线', icon: 'Connection', tone: 'emerald' },
  { label: '今日指令', value: 214, suffix: '条', trend: '高危 0 条', icon: 'Promotion', tone: 'indigo' },
  { label: '待审批操作', value: 2, suffix: '项', trend: '生产变更需双人复核', icon: 'Lock', tone: 'amber' },
]

const entries = [
  {
    title: '运维终端',
    desc: '多环境主机 Web SSH，实时会话审计与命令协同',
    icon: 'Monitor',
    accent: 'cyan',
    path: '/ops/terminal',
  },
  { title: '批量作业', desc: 'Ansible 作业编排与分批执行（待接入）', icon: 'Operation', accent: 'indigo' },
  { title: '变更审批', desc: '高危操作工单与双人复核流（待接入）', icon: 'Stamp', accent: 'amber' },
  { title: '会话审计', desc: '终端录像与命令审计回放（待接入）', icon: 'VideoCamera', accent: 'emerald' },
]
</script>

<template>
  <DomainHome
    title="运维中心"
    description="日常运维操作入口：终端、批量作业、变更管控与操作审计"
    :metrics="metrics"
    :entries="entries"
  />
</template>
