<script setup>
import { computed } from 'vue'

const props = defineProps({
  pipeline: { type: Object, required: true },
})

const statusMeta = {
  success: { label: 'Success', type: 'success', icon: 'CircleCheckFilled', bar: 'bg-emerald-400' },
  running: { label: 'Running', type: 'primary', icon: 'Loading', bar: 'bg-cyan-400' },
  failed: { label: 'Failed', type: 'danger', icon: 'CircleCloseFilled', bar: 'bg-rose-400' },
}

const envTagType = { dev: 'success', staging: 'warning', prod: 'danger' }

const meta = computed(() => statusMeta[props.pipeline.status])

// 流水线阶段：根据 progress 粗略映射，用于可视化编排进度
const stages = ['拉取代码', '构建镜像', '单元测试', '部署发布']
const currentStageIndex = computed(() => {
  if (props.pipeline.status === 'success') return stages.length
  if (props.pipeline.status === 'failed') return Math.max(0, Math.floor(props.pipeline.progress / 26))
  return Math.min(stages.length - 1, Math.floor(props.pipeline.progress / 26))
})
</script>

<template>
  <article
    class="rounded-xl border border-slate-800 bg-slate-900/50 p-5 transition-colors hover:border-slate-700"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <h3 class="truncate text-sm font-semibold text-slate-100">{{ pipeline.name }}</h3>
          <el-tag size="small" :type="envTagType[pipeline.env]" effect="dark">{{ pipeline.env }}</el-tag>
        </div>
        <p class="mt-1 truncate font-mono text-xs text-slate-500">{{ pipeline.repo }}</p>
      </div>
      <el-tag :type="meta.type" effect="dark" class="shrink-0">
        <el-icon class="mr-1" :class="pipeline.status === 'running' ? 'animate-spin' : ''">
          <component :is="meta.icon" />
        </el-icon>
        {{ meta.label }}
      </el-tag>
    </div>

    <!-- 触发信息 -->
    <div class="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
      <span class="inline-flex items-center gap-1">
        <el-icon><Connection /></el-icon>{{ pipeline.branch }}
      </span>
      <span class="font-mono text-slate-500">{{ pipeline.commit }}</span>
      <span class="inline-flex items-center gap-1">
        <el-icon><User /></el-icon>{{ pipeline.actor }}
      </span>
      <span class="inline-flex items-center gap-1">
        <el-icon><Timer /></el-icon>{{ pipeline.duration }}
      </span>
    </div>

    <!-- 阶段编排条 -->
    <div class="mt-4 flex items-center gap-1">
      <template v-for="(stage, index) in stages" :key="stage">
        <div
          class="flex-1 truncate rounded px-2 py-1 text-center text-[11px]"
          :class="
            index < currentStageIndex
              ? 'bg-cyber-500/15 text-cyber-300'
              : pipeline.status === 'failed' && index === currentStageIndex
                ? 'bg-rose-500/15 text-rose-300'
                : 'bg-slate-800/70 text-slate-500'
          "
        >
          {{ stage }}
        </div>
        <el-icon v-if="index < stages.length - 1" class="text-slate-700"><ArrowRight /></el-icon>
      </template>
    </div>

    <!-- 进度条 -->
    <div class="mt-4">
      <div class="mb-1 flex justify-between text-[11px] text-slate-500">
        <span>{{ pipeline.stage }}</span>
        <span>{{ pipeline.progress }}%</span>
      </div>
      <el-progress
        :percentage="pipeline.progress"
        :show-text="false"
        :stroke-width="6"
        :status="pipeline.status === 'failed' ? 'exception' : pipeline.status === 'success' ? 'success' : ''"
      />
    </div>

    <div class="mt-4 flex justify-between border-t border-slate-800 pt-3">
      <span class="text-[11px] text-slate-600">{{ pipeline.startedAt }}</span>
      <div class="flex gap-2">
        <el-button text size="small" class="!text-cyan-400">日志</el-button>
        <el-button text size="small" class="!text-slate-400">详情</el-button>
        <el-button
          v-if="pipeline.status === 'running'"
          text
          size="small"
          class="!text-rose-400"
        >
          终止
        </el-button>
        <el-button
          v-else
          text
          size="small"
          class="!text-indigo-300"
        >
          重跑
        </el-button>
      </div>
    </div>
  </article>
</template>
