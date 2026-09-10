<script setup>
// 通用页面标题栏：保持各视图头部结构一致
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="flex flex-wrap items-start justify-between gap-3">
    <div>
      <h1 class="text-xl font-semibold text-slate-100">{{ title }}</h1>
      <p v-if="description" class="mt-1 text-sm text-slate-500">{{ description }}</p>
    </div>
    <div class="flex items-center gap-2">
      <slot name="extra" />
    </div>
  </div>
</template>
