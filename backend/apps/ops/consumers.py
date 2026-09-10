"""运维终端 WebSocket Consumer（由 core 占位通道迁入运维中心）。"""

import logging

from channels.generic.websocket import JsonWebsocketConsumer

from apps.ops.services.host_service import get_host

logger = logging.getLogger(__name__)


class TerminalConsumer(JsonWebsocketConsumer):
    """Web SSH 通道占位。

    路由：/ws/ops/terminal/<host_id>/?token=<JWT>
    骨架阶段仅回显命令并返回模拟输出；后续在此桥接真实 SSH（如 asyncssh）
    并落审计日志，鉴权由 core.ws.JwtAuthMiddlewareStack 统一完成。
    """

    def connect(self):
        if self.scope["user"].is_anonymous:
            self.close(code=4401)
            return

        self.host_id = self.scope["url_route"]["kwargs"]["host_id"]
        self.host = get_host(self.host_id)
        if self.host is None or self.host["status"] == "offline":
            self.close(code=4404)
            return

        self.group_name = f"ops.terminal.{self.host_id}"
        self.accept()
        self.send_json({
            "type": "connected",
            "request_id": self.scope.get("request_id"),
            "host": self.host,
            "message": f"已连接 {self.host['name']} ({self.host['ip']})，终端通道为占位实现",
        })

    def receive_json(self, content, **kwargs):
        command = (content or {}).get("command", "")
        logger.info("terminal command from %s on %s: %s",
                    self.scope["user"], self.host_id, command)
        self.send_json({
            "type": "output",
            "host_id": self.host_id,
            "command": command,
            "output": f"[stub] {self.host['name']}:~$ {command}\n(真实 SSH 执行链路待接入)",
        })

    def disconnect(self, code):
        logger.info("terminal session closed: host=%s code=%s", self.host_id, code)
