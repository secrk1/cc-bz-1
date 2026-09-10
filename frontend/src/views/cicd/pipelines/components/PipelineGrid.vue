<script setup>
import PipelineCard from './PipelineCard.vue'

defineProps({
  pipelines: { type: Array, required: true },
})
</script>

<template>
  <section v-if="pipelines.length" class="grid grid-cols-1 gap-4 xl:grid-cols-2">
    <PipelineCard v-for="pipeline in pipelines" :key="pipeline.id" :pipeline="pipeline" />
  </section>

  <section v-else class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 py-20">
    <el-icon class="text-5xl text-slate-700"><Box /></el-icon>
    <p class="mt-3 text-sm text-slate-500">没有符合条件的流水线任务</p>
  </section>
</template>
