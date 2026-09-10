<script setup>
import { computed, ref } from 'vue'

const keyword = ref('')
const activeStatus = ref('all')
const activeEnv = ref('all')

const emits = defineEmits(['search'])

const statusOptions = [
  { value: 'all', label: '全部状态' },
  { value: 'success', label: 'Success' },
  { value: 'running', label: 'Running' },
  { value: 'failed', label: 'Failed' },
]
const envOptions = [
  { value: 'all', label: '全部环境' },
  { value: 'dev', label: 'Dev' },
  { value: 'staging', label: 'Staging' },
  { value: 'prod', label: 'Prod' },
]

const payload = computed(() => ({
  keyword: keyword.value,
  status: activeStatus.value,
  env: activeEnv.value,
}))

const triggerSearch = () => emits('search', payload.value)
</script>

<template>
  <section
    class="flex flex-wrap items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-3"
  >
    <el-input
      v-model="keyword"
      placeholder="搜索流水线 / 仓库 / 分支"
      clearable
      class="w-64"
      :prefix-icon="'Search'"
      @keyup.enter="triggerSearch"
      @clear="triggerSearch"
    />
    <el-select v-model="activeStatus" class="w-36" @change="triggerSearch">
      <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
    </el-select>
    <el-select v-model="activeEnv" class="w-36" @change="triggerSearch">
      <el-option v-for="opt in envOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
    </el-select>
    <el-button type="primary" :icon="'Search'" @click="triggerSearch">查询</el-button>
    <div class="flex-1"></div>
    <el-button :icon="'Refresh'">重置</el-button>
    <el-button type="primary" :icon="'VideoPlay'">触发流水线</el-button>
  </section>
</template>
