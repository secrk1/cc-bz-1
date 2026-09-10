<script setup>
import DomainHome from '@/components/domain/DomainHome.vue'

const metrics = [
  { label: '流水线总数', value: 36, suffix: '条', trend: '本周 +4', icon: 'SetUp', tone: 'cyan' },
  { label: '今日构建', value: 128, suffix: '次', trend: '成功率 91.4%', icon: 'CircleCheck', tone: 'emerald' },
  { label: '运行中', value: 2, suffix: '个', trend: '排队 1 个', icon: 'Loading', tone: 'indigo' },
  { label: '失败任务', value: 11, suffix: '个', trend: '需关注', icon: 'Warning', tone: 'rose' },
]

const entries = [
  {
    title: '流水线看板',
    desc: 'CI/CD 任务编排、运行状态与执行耗时全景',
    icon: 'SetUp',
    accent: 'cyan',
    path: '/cicd/pipelines',
  },
  { title: '构建记录', desc: '历史构建、制品与测试报告（待接入）', icon: 'Files', accent: 'indigo' },
  { title: '发布单', desc: '环境发布编排与灰度策略（待接入）', icon: 'Promotion', accent: 'amber' },
  { title: '制品仓库', desc: '镜像与构建产物管理（待接入）', icon: 'Box', accent: 'emerald' },
]
</script>

<template>
  <DomainHome
    title="持续交付"
    description="从代码到生产的流水线编排、构建执行与发布管控"
    :metrics="metrics"
    :entries="entries"
  />
</template>
