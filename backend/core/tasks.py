"""Celery 基础任务。"""

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def heartbeat() -> str:
    """Beat 每分钟触发，用于验证调度链路存活。"""
    logger.info("celery heartbeat ok")
    return "ok"
