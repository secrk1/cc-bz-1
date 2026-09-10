"""业务异步任务占位：流水线执行、集群巡检等长任务在此扩展。"""

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def probe_environment(environment_id: int) -> dict:
    """探测目标集群连通性（骨架占位）。"""
    logger.info("probing environment %s", environment_id)
    return {"environment_id": environment_id, "reachable": False, "reason": "not implemented"}
