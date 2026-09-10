import http from './http'

export const login = (username, password) =>
  http.post('/auth/token/', { username, password })

export const refreshToken = (refresh) =>
  http.post('/auth/token/refresh/', { refresh })
