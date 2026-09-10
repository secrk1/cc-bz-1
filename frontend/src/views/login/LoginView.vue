<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  loading.value = true
  try {
    // 对接后端 POST /api/v1/auth/token/；骨架无后端时给出提示
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch {
    ElMessage.warning('骨架演示：请先启动后端并创建管理员账号')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="relative flex h-full items-center justify-center overflow-hidden bg-slate-950">
    <div class="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-brand-600/20 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-cyber-500/20 blur-3xl"></div>

    <div class="relative w-[400px] rounded-2xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl backdrop-blur">
      <div class="mb-8 flex items-center gap-3">
        <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-cyber-500 text-lg font-bold text-white shadow-glow-indigo">
          N
        </div>
        <div>
          <h1 class="text-lg font-semibold text-slate-100">NexusOps</h1>
          <p class="text-xs text-slate-500">企业级 DevOps 运维平台</p>
        </div>
      </div>

      <el-form label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="账号" class="!mb-4">
          <el-input v-model="form.username" size="large" placeholder="请输入用户名" :prefix-icon="'User'" />
        </el-form-item>
        <el-form-item label="密码" class="!mb-6">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="'Lock'"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button type="primary" size="large" class="w-full" :loading="loading" @click="handleLogin">
          登 录
        </el-button>
      </el-form>

      <p class="mt-6 text-center text-xs text-slate-600">JWT 鉴权 · Access 30min / Refresh 7d</p>
    </div>
  </div>
</template>
