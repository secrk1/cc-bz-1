import http from './http'

const BASE = '/cmdb/environments'

export const fetchEnvironments = (params = {}) => http.get(BASE, { params })

export const createEnvironment = (payload) => http.post(BASE, payload)

export const updateEnvironment = (id, payload) => http.patch(`${BASE}/${id}`, payload)

export const deleteEnvironment = (id) => http.delete(`${BASE}/${id}`)

export const changeEnvironmentStatus = (id, action) => http.post(`${BASE}/${id}/${action}`)
