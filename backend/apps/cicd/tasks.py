"""CI/CD 异步任务占位：流水线触发、构建执行、部署回调等在此扩展。"""

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def run_pipeline(pipeline_id: int, triggered_by: str | None = None) -> dict:
    """执行流水线（骨架占位）。"""
    logger.info("pipeline %s triggered by %s", pipeline_id, triggered_by)
    return {"pipeline_id": pipeline_id, "status": "stub", "message": "execution not implemented"}
