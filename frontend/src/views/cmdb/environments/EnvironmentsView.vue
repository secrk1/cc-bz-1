<script setup>
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import PageHeader from '@/components/PageHeader.vue'
import EnvFilterBar from './components/EnvFilterBar.vue'
import EnvironmentCard from './components/EnvironmentCard.vue'
import EnvironmentFormDialog from './components/EnvironmentFormDialog.vue'
import { seedEnvironments } from './mock'

const environments = ref([...seedEnvironments])
const filters = ref({ keyword: '', envType: 'all', status: 'all' })

const dialogVisible = ref(false)
const editing = ref(null)

const filtered = computed(() =>
  environments.value.filter((item) => {
    const hitType = filters.value.envType === 'all' || item.env_type === filters.value.envType
    const hitStatus = filters.value.status === 'all' || item.status === filters.value.status
    const keyword = filters.value.keyword.trim()
    const hitKeyword = !keyword || item.name.includes(keyword) || item.code.includes(keyword)
    return hitType && hitStatus && hitKeyword
  }),
)

const handleSearch = (payload) => {
  filters.value = payload
}

const openCreate = () => {
  editing.value = null
  dialogVisible.value = true
}

const openEdit = (env) => {
  editing.value = env
  dialogVisible.value = true
}

const handleSubmit = (payload) => {
  if (editing.value) {
    const index = environments.value.findIndex((item) => item.id === editing.value.id)
    environments.value[index] = { ...environments.value[index], ...payload }
    ElMessage.success('环境已更新（骨架本地数据）')
    return
  }
  environments.value.unshift({
    ...payload,
    id: Math.max(...environments.value.map((item) => item.id)) + 1,
    created_at: '刚刚',
  })
  ElMessage.success('环境已创建（骨架本地数据）')
}

const handleToggle = (env) => {
  env.status = env.status === 'active' ? 'inactive' : 'active'
  ElMessage.success(`环境「${env.name}」已${env.status === 'active' ? '启用' : '停用'}`)
}

const handleRemove = async (env) => {
  await ElMessageBox.confirm(`确认删除环境「${env.name}」？该操作不可恢复。`, '危险操作', {
    type: 'warning',
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
  })
  environments.value = environments.value.filter((item) => item.id !== env.id)
  ElMessage.success('环境已删除（骨架本地数据）')
}
</script>

<template>
  <div class="space-y-5">
    <PageHeader title="运行环境管理" description="Dev / Staging / Prod 多环境集群连接配置与生命周期管理" />

    <EnvFilterBar @search="handleSearch" @create="openCreate" />

    <section v-if="filtered.length" class="grid grid-cols-1 gap-4 md:grid-cols-2 2xl:grid-cols-3">
      <EnvironmentCard
        v-for="env in filtered"
        :key="env.id"
        :environment="env"
        @edit="openEdit"
        @toggle="handleToggle"
        @remove="handleRemove"
      />
    </section>

    <section v-else class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 py-20">
      <el-icon class="text-5xl text-slate-700"><Coin /></el-icon>
      <p class="mt-3 text-sm text-slate-500">暂无符合条件的环境配置</p>
      <el-button type="primary" class="mt-4" @click="openCreate">新增第一个环境</el-button>
    </section>

    <EnvironmentFormDialog v-model:visible="dialogVisible" :editing="editing" @submit="handleSubmit" />
  </div>
</template>
