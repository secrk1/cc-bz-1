"""
日志工具：把当前链路 request_id 注入每一条 LogRecord。

Console 与 File Handler 均挂载本过滤器，从而保证
"每条控制台/文件日志前自动打印 request_id"。
"""

import logging

from .context import get_request_id


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True
