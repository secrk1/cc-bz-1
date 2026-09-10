<script setup>
import { computed, ref } from 'vue'

import PageHeader from '@/components/PageHeader.vue'
import FilterBar from './components/FilterBar.vue'
import StatusSummary from './components/StatusSummary.vue'
import PipelineGrid from './components/PipelineGrid.vue'
import { pipelines as source } from './mock'

const filters = ref({ keyword: '', status: 'all', env: 'all' })

const filteredPipelines = computed(() =>
  source.filter((item) => {
    const hitKeyword =
      !filters.value.keyword ||
      item.name.includes(filters.value.keyword) ||
      item.branch.includes(filters.value.keyword) ||
      item.repo.includes(filters.value.keyword)
    const hitStatus = filters.value.status === 'all' || item.status === filters.value.status
    const hitEnv = filters.value.env === 'all' || item.env === filters.value.env
    return hitKeyword && hitStatus && hitEnv
  }),
)

const handleSearch = (payload) => {
  filters.value = payload
}
</script>

<template>
  <div class="space-y-5">
    <PageHeader title="流水线看板" description="CI/CD 任务编排、运行状态与执行耗时全景">
      <template #extra>
        <el-button :icon="'Download'">导出</el-button>
      </template>
    </PageHeader>

    <StatusSummary />
    <FilterBar @search="handleSearch" />
    <PipelineGrid :pipelines="filteredPipelines" />
  </div>
</template>
