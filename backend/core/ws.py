"""
WebSocket 鉴权中间件：从查询串 ?token=<JWT> 校验 access token。

浏览器原生 WebSocket 无法自定义 Authorization 头，因此采用查询串传 token；
生产环境应仅通过 wss:// 访问，避免 token 落入访问日志。
"""

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .context import set_request_id
from .middleware import normalize_incoming_id


@database_sync_to_async
def get_user_from_token(token: str):
    try:
        validated = JWTAuthentication().get_validated_token(token)
        return JWTAuthentication().get_user(validated)
    except (InvalidToken, TokenError):
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = query.get("token", [None])[0]

        # WebSocket 无法自定义请求头：允许前端经 ?request_id= 透传，缺失则生成，
        # 使通道内日志与触发页面的请求链路可串联
        request_id = normalize_incoming_id(query.get("request_id", [None])[0])
        scope["request_id"] = request_id
        set_request_id(request_id)

        scope["user"] = await get_user_from_token(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
