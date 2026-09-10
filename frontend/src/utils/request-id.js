/**
 * 前端 Request-ID 生成器。
 * 优先使用浏览器原生 crypto.randomUUID，旧环境退化为随机 hex。
 */
export function generateRequestId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID().replace(/-/g, '')
  }
  return 'rid-' + Date.now().toString(16) + Math.random().toString(16).slice(2, 10)
}
