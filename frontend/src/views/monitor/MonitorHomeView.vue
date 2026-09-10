<script setup>
// 监控中心工作台：核心指标 + 功能入口 + 实时告警/任务面板
import DomainHome from '@/components/domain/DomainHome.vue'
import AlertFeed from './components/AlertFeed.vue'
import BuildJobPanel from './components/BuildJobPanel.vue'
import { clusterStats } from './mock'

const metrics = clusterStats

const entries = [
  {
    title: '全局资源大盘',
    desc: '集群节点、工作负载与资源水位的跨环境聚合视图',
    icon: 'Odometer',
    accent: 'cyan',
    tag: '当前页',
  },
  { title: '告警中心', desc: '告警规则、屏蔽策略与告警收敛（待接入）', icon: 'Bell', accent: 'amber' },
  { title: '指标查询', desc: 'Prometheus 指标即席查询与图表（待接入）', icon: 'TrendCharts', accent: 'indigo' },
  { title: '日志检索', desc: '聚合日志全文检索与上下文追踪（待接入）', icon: 'Document', accent: 'emerald' },
]
</script>

<template>
  <DomainHome
    title="监控中心"
    description="跨环境聚合的集群健康度、实时告警与交付任务一览"
    :metrics="metrics"
    :entries="entries"
  >
    <template #extra>
      <el-button :icon="'Refresh'">刷新</el-button>
      <el-button type="primary" :icon="'Plus'">新建大盘</el-button>
    </template>

    <div class="grid grid-cols-1 gap-5 xl:grid-cols-5">
      <div class="xl:col-span-2">
        <AlertFeed />
      </div>
      <div class="xl:col-span-3">
        <BuildJobPanel />
      </div>
    </div>
  </DomainHome>
</template>
