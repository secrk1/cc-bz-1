// 主机清单演示数据
export const hosts = [
  { id: 'prod-web-01', name: 'prod-web-01', ip: '10.20.1.11', env: 'prod', os: 'Ubuntu 22.04', status: 'online' },
  { id: 'prod-web-02', name: 'prod-web-02', ip: '10.20.1.12', env: 'prod', os: 'Ubuntu 22.04', status: 'online' },
  { id: 'prod-db-01', name: 'prod-db-01', ip: '10.20.2.10', env: 'prod', os: 'Rocky 9', status: 'busy' },
  { id: 'staging-app-01', name: 'staging-app-01', ip: '10.30.1.21', env: 'staging', os: 'Debian 12', status: 'online' },
  { id: 'staging-worker-01', name: 'staging-worker-01', ip: '10.30.1.22', env: 'staging', os: 'Debian 12', status: 'offline' },
  { id: 'dev-k8s-node-01', name: 'dev-k8s-node-01', ip: '10.40.0.11', env: 'dev', os: 'Ubuntu 22.04', status: 'online' },
  { id: 'dev-k8s-node-02', name: 'dev-k8s-node-02', ip: '10.40.0.12', env: 'dev', os: 'Ubuntu 22.04', status: 'online' },
]

export const envTagType = { dev: 'success', staging: 'warning', prod: 'danger' }
