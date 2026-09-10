<script setup>
import { recentJobs } from '../mock'

const statusMeta = {
  success: { label: 'Success', type: 'success', icon: 'CircleCheckFilled' },
  running: { label: 'Running', type: 'primary', icon: 'Loading' },
  failed: { label: 'Failed', type: 'danger', icon: 'CircleCloseFilled' },
}
</script>

<template>
  <section class="flex h-full flex-col rounded-xl border border-slate-800 bg-slate-900/50">
    <header class="flex items-center justify-between border-b border-slate-800 px-5 py-4">
      <h2 class="text-sm font-semibold text-slate-200">近期构建 / 部署任务</h2>
      <el-radio-group model-value="all" size="small">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="running">运行中</el-radio-button>
      </el-radio-group>
    </header>

    <el-scrollbar class="flex-1">
      <table class="w-full text-left text-sm">
        <thead>
          <tr class="text-xs text-slate-500">
            <th class="px-5 py-2 font-medium">任务</th>
            <th class="px-3 py-2 font-medium">分支</th>
            <th class="px-3 py-2 font-medium">状态</th>
            <th class="px-3 py-2 font-medium">耗时</th>
            <th class="px-5 py-2 font-medium">触发者</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/70">
          <tr v-for="job in recentJobs" :key="job.id" class="hover:bg-slate-800/30">
            <td class="px-5 py-3">
              <p class="font-medium text-slate-200">{{ job.name }}</p>
              <p class="text-xs text-slate-500">{{ job.time }}</p>
            </td>
            <td class="px-3 py-3">
              <el-tag size="small" effect="plain" class="!border-slate-700 !text-slate-400">
                {{ job.branch }}
              </el-tag>
            </td>
            <td class="px-3 py-3">
              <span class="inline-flex items-center gap-1.5">
                <el-icon :class="job.status === 'running' ? 'animate-spin' : ''">
                  <component :is="statusMeta[job.status].icon" />
                </el-icon>
                <el-tag :type="statusMeta[job.status].type" size="small" effect="dark">
                  {{ statusMeta[job.status].label }}
                </el-tag>
              </span>
            </td>
            <td class="px-3 py-3 font-mono text-xs text-slate-400">{{ job.duration }}</td>
            <td class="px-5 py-3 text-slate-400">{{ job.actor }}</td>
          </tr>
        </tbody>
      </table>
    </el-scrollbar>
  </section>
</template>
