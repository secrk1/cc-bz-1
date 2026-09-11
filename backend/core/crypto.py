"""
对称可逆加密工具（仅依赖 Python 标准库，无第三方加密包）。

用途：CMDB 凭据（口令 / SSH 私钥）必须密文落库，禁止明文存储。

算法设计（Encrypt-then-MAC）：
- PBKDF2-HMAC-SHA256（200_000 轮）从主密钥派生 64 字节，
  前 32 字节为加密密钥、后 32 字节为 MAC 密钥，每条密文使用独立随机 salt；
- 流密码采用 HMAC-SHA256 构造 CTR 密钥流，无需 AES 原生支持；
- 密文追加 HMAC-SHA256 认证标签，解密前先验签，密文被篡改即拒绝。

主密钥来源：settings.CMDB_CREDENTIAL_SECRET，缺省回退 settings.SECRET_KEY。
密文格式：``enc$v1$<base64(salt|nonce|ciphertext|tag)>``，带版本前缀，
历史明文 / 空值可被 ``is_encrypted`` 明确识别。
"""

from __future__ import annotations

import base64
import hashlib
import hmac

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_PREFIX = "enc$v1$"
_KDF_ITERATIONS = 200_000
_SALT_LEN = 16
_NONCE_LEN = 16
_TAG_LEN = 32
_BLOCK_LEN = 32  # HMAC-SHA256 单块输出长度


class CipherError(Exception):
    """密文非法或验签失败。"""


def _master_secret() -> bytes:
    secret = getattr(settings, "CMDB_CREDENTIAL_SECRET", None) or settings.SECRET_KEY
    if not secret:
        raise ImproperlyConfigured("CMDB_CREDENTIAL_SECRET / SECRET_KEY 未配置，无法加解密凭据")
    return secret.encode("utf-8")


def _derive_keys(salt: bytes) -> tuple[bytes, bytes]:
    derived = hashlib.pbkdf2_hmac(
        "sha256", _master_secret(), salt, _KDF_ITERATIONS, dklen=64,
    )
    return derived[:32], derived[32:]


def _keystream(enc_key: bytes, nonce: bytes, length: int) -> bytes:
    """以 HMAC-SHA256(enc_key, nonce || counter_be64) 生成 CTR 密钥流。"""
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = hmac.new(
            enc_key, nonce + counter.to_bytes(8, "big"), hashlib.sha256,
        ).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:length])


def _xor(data: bytes, stream: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data, stream))


def is_encrypted(value: str | None) -> bool:
    return bool(value) and value.startswith(_PREFIX)


def encrypt(plaintext: str | None) -> str | None:
    if plaintext is None or plaintext == "":
        return plaintext
    raw = plaintext.encode("utf-8")
    salt = _random_bytes(_SALT_LEN)
    nonce = _random_bytes(_NONCE_LEN)
    enc_key, mac_key = _derive_keys(salt)
    ciphertext = _xor(raw, _keystream(enc_key, nonce, len(raw)))
    tag = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()
    blob = base64.b64encode(salt + nonce + ciphertext + tag).decode("ascii")
    return f"{_PREFIX}{blob}"


def decrypt(token: str | None) -> str | None:
    if token is None or token == "":
        return token
    if not is_encrypted(token):
        # 兼容历史明文：原样返回，由上层决定是否轮换
        return token
    try:
        blob = base64.b64decode(token[len(_PREFIX):], validate=True)
    except Exception as exc:  # noqa: BLE001
        raise CipherError("凭据密文编码非法") from exc
    if len(blob) < _SALT_LEN + _NONCE_LEN + _TAG_LEN:
        raise CipherError("凭据密文长度非法")
    salt = blob[:_SALT_LEN]
    nonce = blob[_SALT_LEN:_SALT_LEN + _NONCE_LEN]
    tag = blob[-_TAG_LEN:]
    ciphertext = blob[_SALT_LEN + _NONCE_LEN:-_TAG_LEN]
    enc_key, mac_key = _derive_keys(salt)
    expected = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise CipherError("凭据密文验签失败，数据可能已被篡改")
    raw = _xor(ciphertext, _keystream(enc_key, nonce, len(ciphertext)))
    return raw.decode("utf-8")


def _random_bytes(length: int) -> bytes:
    import os

    return os.urandom(length)
