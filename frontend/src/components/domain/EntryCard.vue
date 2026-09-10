<script setup>
import { computed } from 'vue'

const props = defineProps({
  entry: { type: Object, required: true },
})

const accent = computed(() => props.entry.accent || 'cyan')
const accentText = {
  cyan: 'text-cyber-400 group-hover:text-cyber-300',
  indigo: 'text-brand-400 group-hover:text-brand-100',
  emerald: 'text-emerald-400 group-hover:text-emerald-300',
  amber: 'text-amber-400 group-hover:text-amber-300',
}
</script>

<template>
  <component
    :is="entry.path ? 'router-link' : 'div'"
    :to="entry.path || undefined"
    class="group flex items-start gap-4 rounded-xl border border-slate-800 bg-slate-900/50 p-5 transition-all hover:-translate-y-0.5 hover:border-slate-700 hover:shadow-glow"
    :class="!entry.path ? 'cursor-not-allowed opacity-60 hover:translate-y-0 hover:shadow-none' : ''"
  >
    <div class="rounded-lg bg-slate-800/80 p-2.5 transition-colors group-hover:bg-slate-800">
      <el-icon class="text-xl" :class="accentText[accent]"><component :is="entry.icon" /></el-icon>
    </div>
    <div class="min-w-0 flex-1">
      <div class="flex items-center gap-2">
        <h3 class="text-sm font-semibold text-slate-200">{{ entry.title }}</h3>
        <el-tag v-if="entry.tag" size="small" type="info" effect="dark">{{ entry.tag }}</el-tag>
      </div>
      <p class="mt-1 text-xs leading-5 text-slate-500">{{ entry.desc }}</p>
    </div>
    <el-icon v-if="entry.path" class="mt-1 text-slate-600 transition-transform group-hover:translate-x-0.5">
      <ArrowRight />
    </el-icon>
  </component>
</template>
