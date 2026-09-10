import http from './http'
import { generateRequestId } from '@/utils/request-id'

// 运维中心：主机清单与 Web 终端
export const fetchHosts = (params = {}) => http.get('/ops/hosts', { params })

// WebSocket 终端地址（Daphne ASGI 网关）
// token 走查询串由 core.ws 中间件校验；request_id 一并透传以串联通道日志
export const buildTerminalSocketUrl = (hostId, token) => {
  const requestId = generateRequestId()
  return `${wsBase()}/ws/ops/terminal/${hostId}/?token=${encodeURIComponent(token)}&request_id=${requestId}`
}

function wsBase() {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}`
}
