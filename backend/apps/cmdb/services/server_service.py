"""Service 层：服务器资产业务逻辑（规格 / IP / 环境 / 运行状态）。"""

from django.db.models import Q
from django.db import transaction

from apps.cmdb.models import Server

from .base import BaseCrudService
from core.exceptions import BizException


class ServerService(BaseCrudService):
    model = Server
    not_found_message = "服务器不存在"
    conflict_message = "主机名或管理 IP 已存在"

    @staticmethod
    def list_servers(*, environment_id: int | None = None,
                     status: str | None = None,
                     provider: str | None = None,
                     hostname: str | None = None,
                     ip_address: str | None = None,
                     keyword: str | None = None):
        """
        服务器列表：
        - keyword 同时匹配主机名 / 管理 IP / 内网 IP；
        - hostname / ip_address 为 fast-crud 单列模糊搜索；
        - 支持环境 / 运行状态 / 主机类型过滤。
        """
        qs = Server.objects.select_related("environment")
        if environment_id:
            qs = qs.filter(environment_id=environment_id)
        if status:
            qs = qs.filter(status=status)
        if provider:
            qs = qs.filter(provider=provider)
        if hostname:
            qs = qs.filter(hostname__icontains=hostname)
        if ip_address:
            qs = qs.filter(
                Q(ip_address__icontains=ip_address)
                | Q(private_ip__icontains=ip_address)
            )
        if keyword:
            qs = qs.filter(
                Q(hostname__icontains=keyword)
                | Q(ip_address__icontains=keyword)
                | Q(private_ip__icontains=keyword)
            )
        return qs.order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def create_server(payload: dict, owner=None) -> Server:
        return ServerService.create(payload, owner_field="owner", owner=owner)

    @staticmethod
    @transaction.atomic
    def change_status(pk: int, target_status: str) -> Server:
        if target_status not in dict(Server.Status.choices):
            raise BizException(f"非法服务器运行状态: {target_status}")
        server = ServerService.get(pk)
        # 已下线资产不允许直接回到运行态，需走重新纳管流程
        if (server.status == Server.Status.RETIRED
                and target_status != Server.Status.RETIRED):
            raise BizException("已下线服务器不允许直接变更状态，请重新纳管")
        server.status = target_status
        server.save(update_fields=["status", "updated_at"])
        return server
