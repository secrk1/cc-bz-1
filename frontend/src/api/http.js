import axios from 'axios'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'
import { generateRequestId } from '@/utils/request-id'
import router from '@/router'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
})

// 请求拦截：注入全链路 X-Request-ID（重试请求保留原 ID）
http.interceptors.request.use((config) => {
  if (!config.headers['X-Request-ID']) {
    config.headers['X-Request-ID'] = generateRequestId()
  }
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

// 提取本次链路 ID：优先后端回传响应头，其次请求时生成的
const pickRequestId = (responseOrConfig) =>
  responseOrConfig?.headers?.['x-request-id'] ||
  responseOrConfig?.headers?.['X-Request-ID'] ||
  responseOrConfig?.config?.headers?.['X-Request-ID'] ||
  '-'

// 响应拦截：解包统一信封 { code, message, data, request_id }
http.interceptors.response.use(
  (response) => {
    const requestId = pickRequestId(response)
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body.data
      console.error(`[Request ${requestId}] 业务错误:`, body)
      ElMessage.error(`${body.message || '业务处理失败'}（ID: ${requestId.slice(0, 8)}）`)
      return Promise.reject(Object.assign(new Error(body.message), { requestId }))
    }
    // simplejwt 等非信封接口（如 token 端点）原样返回
    return body
  },
  async (error) => {
    const { response, config } = error
    const auth = useAuthStore()
    const requestId = pickRequestId(response) || config?.headers?.['X-Request-ID'] || '-'

    // access 过期时尝试用 refresh 静默续期一次（refresh 请求自身失败不再重试，避免死循环）
    const isRefreshCall = config.url?.includes('/auth/token/refresh')
    if (response?.status === 401 && !config._retried && !isRefreshCall && auth.refreshToken) {
      config._retried = true
      try {
        await auth.refresh()
        config.headers.Authorization = `Bearer ${auth.accessToken}`
        return http(config)
      } catch {
        auth.clear()
        router.push('/login')
      }
    }

    const envelope = response?.data
    const message = envelope?.message || error.message || '网络异常'
    // 前端侧留全量 ID 日志，弹窗展示短 ID，用户报障时可凭此前 8 位定位
    console.error(`[Request ${requestId}] ${config?.method?.toUpperCase()} ${config?.url}`, {
      status: response?.status,
      data: envelope,
    })
    ElMessage.error(`${message}（ID: ${requestId.slice(0, 8)}）`)
    if (response?.status === 401) router.push('/login')
    return Promise.reject(Object.assign(error, { requestId }))
  },
)

export default http
