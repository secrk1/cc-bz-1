// 大盘演示数据（骨架阶段前端 mock，后续替换为 API）
export const clusterStats = [
  { key: 'nodes', label: '集群节点', value: 48, suffix: '台', trend: '+2', icon: 'Cpu', tone: 'cyan' },
  { key: 'pods', label: '运行 Pod', value: 1286, suffix: '个', trend: '+34', icon: 'Box', tone: 'indigo' },
  { key: 'health', label: '集群健康度', value: 99.2, suffix: '%', trend: 'stable', icon: 'CircleCheck', tone: 'emerald' },
  { key: 'alerts', label: '活动告警', value: 7, suffix: '条', trend: '-3', icon: 'Warning', tone: 'amber' },
]

export const alertFeed = [
  { id: 1, level: 'critical', title: 'prod 节点 node-17 磁盘使用率 92%', source: 'Prometheus', time: '2 分钟前' },
  { id: 2, level: 'warning', title: 'staging 命名空间内存 Request 超 85%', source: 'K8s Audit', time: '9 分钟前' },
  { id: 3, level: 'warning', title: '流水线 payment-svc #231 构建耗时异常偏长', source: 'CI Engine', time: '18 分钟前' },
  { id: 4, level: 'info', title: 'prod 完成滚动发布 gateway v2.4.1', source: 'Argo CD', time: '32 分钟前' },
  { id: 5, level: 'critical', title: 'Redis 主从同步延迟超过 5s', source: 'Redis Exporter', time: '45 分钟前' },
]

export const recentJobs = [
  { id: 1, name: 'gateway', branch: 'release/2.4', status: 'success', duration: '3m 12s', actor: 'ci-bot', time: '10:21' },
  { id: 2, name: 'payment-svc', branch: 'main', status: 'running', duration: '2m 05s', actor: 'zhang.san', time: '10:18' },
  { id: 3, name: 'user-center', branch: 'feature/login', status: 'failed', duration: '1m 47s', actor: 'li.si', time: '10:05' },
  { id: 4, name: 'order-svc', branch: 'main', status: 'success', duration: '4m 38s', actor: 'ci-bot', time: '09:52' },
  { id: 5, name: 'data-pipeline', branch: 'hotfix/etl', status: 'running', duration: '5m 51s', actor: 'wang.wu', time: '09:40' },
  { id: 6, name: 'notify-worker', branch: 'main', status: 'success', duration: '2m 02s', actor: 'ci-bot', time: '09:31' },
]
