import { defineStore } from 'pinia'

const ENVIRONMENTS = [
  { value: 'dev', label: 'Dev · 开发集群', tagType: 'success' },
  { value: 'staging', label: 'Staging · 预发集群', tagType: 'warning' },
  { value: 'prod', label: 'Prod · 生产集群', tagType: 'danger' },
]

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: false,
    currentEnv: localStorage.getItem('nexusops.env') || 'dev',
  }),
  getters: {
    environments: () => ENVIRONMENTS,
    currentEnvMeta(state) {
      return ENVIRONMENTS.find((item) => item.value === state.currentEnv) || ENVIRONMENTS[0]
    },
  },
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    setCurrentEnv(env) {
      this.currentEnv = env
      localStorage.setItem('nexusops.env', env)
    },
  },
})
