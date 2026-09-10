"""
运维主机 Service。

骨架阶段维护静态主机清单；规模化后替换为 CMDB 聚合查询
（跨 apps.cmdb 的资源模型组装），View 不感知数据来源。
"""

# 占位清单：后续由 apps.cmdb 主机模型 + 实时心跳状态取代
_DEMO_HOSTS = [
    {"id": "prod-web-01", "name": "prod-web-01", "ip": "10.20.1.11",
     "env": "prod", "os": "Ubuntu 22.04", "status": "online"},
    {"id": "prod-web-02", "name": "prod-web-02", "ip": "10.20.1.12",
     "env": "prod", "os": "Ubuntu 22.04", "status": "online"},
    {"id": "prod-db-01", "name": "prod-db-01", "ip": "10.20.2.10",
     "env": "prod", "os": "Rocky 9", "status": "busy"},
    {"id": "staging-app-01", "name": "staging-app-01", "ip": "10.30.1.21",
     "env": "staging", "os": "Debian 12", "status": "online"},
    {"id": "staging-worker-01", "name": "staging-worker-01", "ip": "10.30.1.22",
     "env": "staging", "os": "Debian 12", "status": "offline"},
    {"id": "dev-k8s-node-01", "name": "dev-k8s-node-01", "ip": "10.40.0.11",
     "env": "dev", "os": "Ubuntu 22.04", "status": "online"},
    {"id": "dev-k8s-node-02", "name": "dev-k8s-node-02", "ip": "10.40.0.12",
     "env": "dev", "os": "Ubuntu 22.04", "status": "online"},
]


def list_hosts(*, env: str | None = None, keyword: str | None = None) -> list[dict]:
    hosts = _DEMO_HOSTS
    if env:
        hosts = [h for h in hosts if h["env"] == env]
    if keyword:
        hosts = [h for h in hosts if keyword in h["name"] or keyword in h["ip"]]
    return hosts


def get_host(host_id: str) -> dict | None:
    return next((h for h in _DEMO_HOSTS if h["id"] == host_id), None)
