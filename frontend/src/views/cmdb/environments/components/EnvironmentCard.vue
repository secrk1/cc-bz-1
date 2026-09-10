<script setup>
import { envTypeMeta, statusMeta } from '../mock'

defineProps({
  environment: { type: Object, required: true },
})

const emits = defineEmits(['edit', 'toggle', 'remove'])
</script>

<template>
  <article
    class="flex flex-col rounded-xl border bg-slate-900/50 p-5 transition-all hover:-translate-y-0.5 hover:shadow-glow"
    :class="envTypeMeta[environment.env_type].accent"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800">
          <el-icon class="text-xl text-cyber-400"><Coin /></el-icon>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-slate-100">{{ environment.name }}</h3>
          <p class="font-mono text-xs text-slate-500">{{ environment.code }}</p>
        </div>
      </div>
      <div class="flex flex-col items-end gap-1.5">
        <el-tag :type="envTypeMeta[environment.env_type].tag" size="small" effect="dark">
          {{ envTypeMeta[environment.env_type].label }}
        </el-tag>
        <span class="inline-flex items-center gap-1 text-[11px] text-slate-400">
          <span class="h-1.5 w-1.5 rounded-full" :class="statusMeta[environment.status].dot"></span>
          {{ statusMeta[environment.status].label }}
        </span>
      </div>
    </div>

    <p class="mt-4 line-clamp-2 min-h-[2.5rem] text-xs leading-5 text-slate-400">
      {{ environment.description || '暂无环境描述' }}
    </p>

    <dl class="mt-4 space-y-2 rounded-lg bg-slate-950/50 p-3 text-xs">
      <div class="flex items-center gap-2">
        <dt class="w-16 shrink-0 text-slate-500">API Server</dt>
        <dd class="truncate font-mono text-cyber-300">{{ environment.cluster_endpoint }}</dd>
      </div>
      <div class="flex items-center gap-2">
        <dt class="w-16 shrink-0 text-slate-500">命名空间</dt>
        <dd class="font-mono text-slate-300">{{ environment.namespace }}</dd>
      </div>
      <div class="flex items-center gap-2">
        <dt class="w-16 shrink-0 text-slate-500">创建时间</dt>
        <dd class="text-slate-400">{{ environment.created_at }}</dd>
      </div>
    </dl>

    <div class="mt-4 flex items-center justify-end gap-1 border-t border-slate-800 pt-3">
      <el-button text size="small" class="!text-cyan-400" @click="emits('edit', environment)">
        编辑
      </el-button>
      <el-button text size="small" class="!text-amber-300" @click="emits('toggle', environment)">
        {{ environment.status === 'active' ? '停用' : '启用' }}
      </el-button>
      <el-button text size="small" class="!text-rose-400" @click="emits('remove', environment)">
        删除
      </el-button>
    </div>
  </article>
</template>
