import { defineStore } from 'pinia'

import { login as loginApi, refreshToken } from '@/api/auth'

const ACCESS_KEY = 'nexusops.access'
const REFRESH_KEY = 'nexusops.refresh'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem(ACCESS_KEY) || '',
    refreshTokenValue: localStorage.getItem(REFRESH_KEY) || '',
    username: localStorage.getItem('nexusops.username') || '',
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
  },
  actions: {
    async login(username, password) {
      const data = await loginApi(username, password)
      this.setTokens(data.access, data.refresh, username)
    },
    async refresh() {
      const data = await refreshToken(this.refreshTokenValue)
      this.accessToken = data.access
      localStorage.setItem(ACCESS_KEY, data.access)
    },
    setTokens(access, refresh, username) {
      this.accessToken = access
      this.refreshTokenValue = refresh
      this.username = username
      localStorage.setItem(ACCESS_KEY, access)
      localStorage.setItem(REFRESH_KEY, refresh)
      localStorage.setItem('nexusops.username', username)
    },
    clear() {
      this.accessToken = ''
      this.refreshTokenValue = ''
      this.username = ''
      localStorage.removeItem(ACCESS_KEY)
      localStorage.removeItem(REFRESH_KEY)
      localStorage.removeItem('nexusops.username')
    },
  },
})
