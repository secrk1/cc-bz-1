import http from './http'

const BASE = '/cicd/pipelines'

export const fetchPipelines = (params = {}) => http.get(BASE, { params })

export const fetchPipeline = (id) => http.get(`${BASE}/${id}`)

export const createPipeline = (payload) => http.post(BASE, payload)
