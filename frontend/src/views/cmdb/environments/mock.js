// 运行环境初始演示数据；接入后端后由 /environments 接口替换
export const seedEnvironments = [
  {
    id: 1,
    name: '开发集群',
    code: 'dev-k8s',
    env_type: 'dev',
    cluster_endpoint: 'https://k8s-dev.nexusops.local:6443',
    namespace: 'nexus-dev',
    description: '研发自测与联调环境，资源超卖，允许快速回滚',
    status: 'active',
    created_at: '2026-08-12 09:30:00',
  },
  {
    id: 2,
    name: '预发集群',
    code: 'staging-k8s',
    env_type: 'staging',
    cluster_endpoint: 'https://k8s-staging.nexusops.local:6443',
    namespace: 'nexus-staging',
    description: '与生产同构，用于发布验收与压测',
    status: 'maintaining',
    created_at: '2026-08-20 14:02:11',
  },
  {
    id: 3,
    name: '生产集群-华东',
    code: 'prod-k8s-east',
    env_type: 'prod',
    cluster_endpoint: 'https://k8s-prod-east.nexusops.io:6443',
    namespace: 'nexus-prod',
    description: '核心交易生产集群，多可用区部署，变更需审批',
    status: 'active',
    created_at: '2026-07-01 10:00:00',
  },
  {
    id: 4,
    name: '生产集群-华北（容灾）',
    code: 'prod-k8s-north',
    env_type: 'prod',
    cluster_endpoint: 'https://k8s-prod-north.nexusops.io:6443',
    namespace: 'nexus-prod',
    description: '异地容灾集群，常态承载 20% 只读流量',
    status: 'inactive',
    created_at: '2026-07-15 16:20:45',
  },
]

export const envTypeMeta = {
  dev: { label: 'Dev', tag: 'success', accent: 'border-emerald-500/30', dot: 'bg-emerald-400' },
  staging: { label: 'Staging', tag: 'warning', accent: 'border-amber-500/30', dot: 'bg-amber-400' },
  prod: { label: 'Prod', tag: 'danger', accent: 'border-rose-500/30', dot: 'bg-rose-400' },
}

export const statusMeta = {
  active: { label: '可用', tag: 'success', dot: 'bg-emerald-400' },
  inactive: { label: '停用', tag: 'info', dot: 'bg-slate-500' },
  maintaining: { label: '维护中', tag: 'warning', dot: 'bg-amber-400' },
}
