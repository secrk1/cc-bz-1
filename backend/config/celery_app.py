"""Celery 应用实例。

通过 ``config.celery_app`` 暴露给 ``celery -A config worker/beat`` 使用，
在 Django 启动时自动发现各应用 ``tasks.py``，并在发布/执行任务时透传
request_id，使异步任务日志与触发它的 HTTP 请求链路可串联。
"""

import os
import uuid

from celery import Celery
from celery.signals import before_task_publish, task_prerun
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("devops_platform")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# 基础调度示例（业务侧可继续通过 django-celery-beat 动态注册）
app.conf.beat_schedule = {
    "heartbeat-every-minute": {
        "task": "core.tasks.heartbeat",
        "schedule": crontab(),
    },
}


@before_task_publish.connect
def _publish_request_id(headers=None, **_kwargs):
    """HTTP 请求内触发任务时，把当前 request_id 放进任务消息头。"""
    from core.context import get_request_id

    request_id = get_request_id()
    if headers is not None and request_id != "-":
        headers["request_id"] = request_id


@task_prerun.connect
def _restore_request_id(task=None, **_kwargs):
    """任务执行前恢复发布方 request_id；缺失（如 beat 自发）则新生成。"""
    from core.context import set_request_id

    request_id = None
    raw_headers = getattr(getattr(task, "request", None), "headers", None) or {}
    request_id = raw_headers.get("request_id")
    set_request_id(request_id or uuid.uuid4().hex)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
