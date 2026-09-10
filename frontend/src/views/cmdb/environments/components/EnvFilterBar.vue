<script setup>
import { ref } from 'vue'

const keyword = ref('')
const envType = ref('all')
const status = ref('all')

const emits = defineEmits(['search', 'create'])

const typeOptions = [
  { value: 'all', label: '全部类型' },
  { value: 'dev', label: 'Dev' },
  { value: 'staging', label: 'Staging' },
  { value: 'prod', label: 'Prod' },
]
const statusOptions = [
  { value: 'all', label: '全部状态' },
  { value: 'active', label: '可用' },
  { value: 'maintaining', label: '维护中' },
  { value: 'inactive', label: '停用' },
]

const emitSearch = () =>
  emits('search', { keyword: keyword.value, envType: envType.value, status: status.value })
</script>

<template>
  <section
    class="flex flex-wrap items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-3"
  >
    <el-input
      v-model="keyword"
      placeholder="搜索环境名称 / 标识"
      clearable
      class="w-60"
      :prefix-icon="'Search'"
      @keyup.enter="emitSearch"
      @clear="emitSearch"
    />
    <el-select v-model="envType" class="w-32" @change="emitSearch">
      <el-option v-for="opt in typeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
    </el-select>
    <el-select v-model="status" class="w-32" @change="emitSearch">
      <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
    </el-select>
    <el-button type="primary" :icon="'Search'" @click="emitSearch">查询</el-button>
    <div class="flex-1"></div>
    <el-button type="primary" :icon="'Plus'" @click="emits('create')">新增环境</el-button>
  </section>
</template>
