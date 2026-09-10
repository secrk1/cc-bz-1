<script setup>
// 子系统标准工作台骨架：页头 + 核心指标卡片 + 功能入口，附加面板走默认插槽
import PageHeader from '@/components/PageHeader.vue'
import MetricCard from './MetricCard.vue'
import EntryCard from './EntryCard.vue'

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  metrics: { type: Array, default: () => [] },
  entries: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="space-y-5">
    <PageHeader :title="title" :description="description">
      <template #extra>
        <slot name="extra" />
      </template>
    </PageHeader>

    <section v-if="metrics.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" />
    </section>

    <section>
      <h2 class="mb-3 text-sm font-semibold text-slate-300">功能入口</h2>
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 2xl:grid-cols-3">
        <EntryCard v-for="entry in entries" :key="entry.title" :entry="entry" />
      </div>
    </section>

    <slot />
  </div>
</template>
