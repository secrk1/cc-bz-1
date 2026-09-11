<script setup>
import { nextTick, ref } from 'vue'
import { useFsAsync, useFsRef } from '@fast-crud/fast-crud'

import http from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import { buildServerCrudOptions } from './crud'

// useFsRef 创建绑定引用；useFsAsync 支持先拉取环境字典再构建 crudOptions，
// 保证“纳管服务器”表单的环境下拉首屏即有数据（本地字典，非懒加载）。
const { crudRef, crudBinding, crudExpose, context } = useFsRef()
const ready = ref(false)

useFsAsync({
  crudRef,
  crudBinding,
  crudExpose,
  context,
  async createCrudOptions() {
    const res = await http.get('/cmdb/environments', { params: { page_size: 100 } })
    const environmentOptions = (res.items || []).map((env) => ({
      value: env.id,
      label: `${env.name}（${env.code}）`,
    }))
    return { crudOptions: buildServerCrudOptions(environmentOptions) }
  },
}).then(async () => {
  ready.value = true
  await nextTick()
  crudExpose.doRefresh()
})
</script>

<template>
  <!-- 占满 main 可视高度，标题固定、表格面板弹性填满（页面自身不整体滚动） -->
  <div class="flex h-full min-h-0 flex-col gap-4">
    <PageHeader
      title="服务器资产"
      description="服务器规格、IP、所属环境与运行状态，支持预分配与实例纳管"
    />
    <!-- 深色容器，与平台深色框架 / Element Plus 暗色表格统一，不出现黑白拼接 -->
    <div
      class="server-crud-panel flex min-h-0 flex-1 flex-col rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg"
    >
      <fs-crud v-if="ready" ref="crudRef" v-bind="crudBinding" class="min-h-0 flex-1" />
    </div>
  </div>
</template>

<style scoped>
/*
 * 打通 fast-crud 容器的 flex 高度链：
 * 搜索/操作区与分页固定，表格区弹性填满剩余高度。
 * 表格本体交给 el-table 的 height:'auto'（在 crudOptions.table 配置），
 * 由其监听父容器高度并实现表头固定、表体内部滚动，这里不要覆盖其高度。
 */
.server-crud-panel :deep(.fs-crud-container) {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
}
.server-crud-panel :deep(.fs-crud-header),
.server-crud-panel :deep(.fs-crud-footer) {
  flex-shrink: 0;
}
.server-crud-panel :deep(.fs-crud-table) {
  flex: 1 1 auto;
  min-height: 0;
}
.server-crud-panel :deep(.fs-container) {
  background: transparent;
}
</style>
