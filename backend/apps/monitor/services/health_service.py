"""
平台组件探活 Service（由 core 迁入监控中心，统一负责基础设施健康度）。

仅返回结构化结果，不感知 HTTP；由 View 负责信封包装。
"""

import socket
import time

import redis
from celery import current_app
from django.db import connections


def check_database() -> dict:
    try:
        started = time.perf_counter()
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
        latency = round((time.perf_counter() - started) * 1000, 2)
        return {"name": "database", "status": "up", "latency_ms": latency}
    except Exception as exc:  # noqa: BLE001
        return {"name": "database", "status": "down", "error": str(exc)}


def check_redis() -> dict:
    """直连 Redis 做 PING + 写读校验，避免误用本地内存缓存造成“假活”。"""
    from django.conf import settings

    started = time.perf_counter()
    client = None
    try:
        client = redis.Redis.from_url(
            settings.HEALTH_CHECK["REDIS_URL"],
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        client.set("healthz:probe", "1", ex=10)
        if client.get("healthz:probe") != b"1":
            raise RuntimeError("redis readback mismatch")
        latency = round((time.perf_counter() - started) * 1000, 2)
        return {"name": "redis", "status": "up", "latency_ms": latency}
    except Exception as exc:  # noqa: BLE001
        return {"name": "redis", "status": "down", "error": str(exc)}
    finally:
        if client is not None:
            client.close()


def check_celery(timeout: float = 2.0) -> dict:
    """通过 Celery inspect ping 探测至少一个在线 worker。"""
    try:
        inspector = current_app.control.inspect(timeout=timeout)
        ping = inspector.ping()
        if ping:
            return {
                "name": "celery",
                "status": "up",
                "workers": len(ping),
                "hostname": socket.gethostname(),
            }
        return {"name": "celery", "status": "down", "error": "no workers responded"}
    except Exception as exc:  # noqa: BLE001
        return {"name": "celery", "status": "down", "error": str(exc)}


def collect_health(include_celery: bool = True) -> dict:
    """聚合健康状态。

    - include_celery=True：完整探针（运维观测用，含 worker ping）；
    - include_celery=False：就绪探针（仅 DB+Redis），供容器健康检查使用，
      避免 celery-worker 依赖 web 健康、而 web 又在等待 worker 响应的启动死锁。
    """
    from django.conf import settings

    checks = [check_database(), check_redis()]
    if include_celery:
        checks.append(check_celery(settings.HEALTH_CHECK["CELERY_TIMEOUT_SECONDS"]))
    healthy = all(item["status"] == "up" for item in checks)
    return {"status": "healthy" if healthy else "degraded", "checks": checks}


def collect_liveness() -> dict:
    """存活探针：进程可响应即存活，不依赖任何外部组件。"""
    return {"status": "alive", "checks": [{"name": "process", "status": "up"}]}
