<script setup>
import DomainHome from '@/components/domain/DomainHome.vue'

const metrics = [
  { label: '纳管环境', value: 5, suffix: '套', trend: 'Dev / SIT / UAT / Pre / Prod', icon: 'Coin', tone: 'cyan' },
  { label: '集群资源池', value: 12, suffix: '个', trend: '近 30 天 +2', icon: 'Grid', tone: 'indigo' },
  { label: '主机资产', value: 326, suffix: '台', trend: '在线率 98.2%', icon: 'Cpu', tone: 'emerald' },
  { label: '配置变更', value: 18, suffix: '次/周', trend: '待审计 2 项', icon: 'EditPen', tone: 'amber' },
]

const entries = [
  {
    title: '运行环境管理',
    desc: 'Dev / SIT / UAT / Pre / Prod 五套环境连接配置与生命周期',
    icon: 'Coin',
    accent: 'cyan',
    path: '/cmdb/environments',
  },
  {
    title: '服务器资产',
    desc: '服务器规格、IP、所属环境与运行状态台账（fast-crud）',
    icon: 'Cpu',
    accent: 'indigo',
    path: '/cmdb/servers',
  },
  { title: '资源拓扑', desc: '服务 - 集群 - 节点拓扑可视化（待接入）', icon: 'Share', accent: 'emerald' },
  { title: '配置项审计', desc: 'CI 变更历史与一致性巡检（待接入）', icon: 'List', accent: 'amber' },
]
</script>

<template>
  <DomainHome
    title="配置中心"
    description="统一管理多环境集群、主机资产与配置项，作为平台资源事实来源"
    :metrics="metrics"
    :entries="entries"
  />
</template>
