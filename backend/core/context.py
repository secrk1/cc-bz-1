"""
请求级上下文变量。

基于 contextvars 在同一请求/任务链路内隐式传递 request_id，
业务代码无需显式传参，日志过滤器与响应信封均可读取。
"""

import contextvars

# 默认值 "-" 让无请求上下文（如启动阶段、定时任务未设置时）的日志也能正常格式化
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def set_request_id(value: str) -> None:
    request_id_ctx.set(value)


def get_request_id() -> str:
    return request_id_ctx.get()
