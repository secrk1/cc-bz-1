"""
项目全局配置。

硬性规范：
- 不注册 django.contrib.admin / django.contrib.messages，整个工程保持无 Admin 纯净后端；
- DRF 默认认证类为 simplejwt 的 JWTAuthentication；
- 通过 django-environ 读取环境变量，12-Factor 友好。
"""

from datetime import timedelta
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# 路径与环境变量
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["*"]),
    DJANGO_SECRET_KEY=(str, "insecure-dev-only-change-me"),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:5173", "http://127.0.0.1:5173"]),
)
env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# CMDB 凭据密文落库的独立主密钥（缺省回退 SECRET_KEY，生产环境建议单独配置）
CMDB_CREDENTIAL_SECRET = env("CMDB_CREDENTIAL_SECRET", default=None)

# ---------------------------------------------------------------------------
# 应用注册 —— 刻意不包含 django.contrib.admin / django.contrib.messages
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "daphne",  # 必须置于内置 staticfiles 之前以接管 runserver（ASGI）
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",

    # 第三方
    "rest_framework",
    "corsheaders",
    "channels",
    "django_celery_beat",

    # 本平台应用：core 为技术底座，其余为五大领域子系统
    "core",
    "apps.cmdb",      # 配置中心
    "apps.ops",       # 运维中心
    "apps.cicd",      # 持续交付
    "apps.monitor",   # 监控中心
]

MIDDLEWARE = [
    # 最外层：生成/回收 X-Request-ID，保证其后所有环节（含异常兜底）均可取到
    "core.middleware.RequestIdMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # 无 Admin：不注册 django.contrib.messages.middleware.MessageMiddleware
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 全局未捕获异常兜底（DRF 之外的异常统一信封输出）
    "core.middleware.GlobalExceptionMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                # 无 Admin：不注册 messages 上下文处理器
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# 数据库 —— PostgreSQL
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://devops:devops@postgres:5432/devops_platform",
    )
}

# ---------------------------------------------------------------------------
# 国际化 / 静态资源
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# 鉴权（本平台为纯 JWT API，不使用 Session 认证；保留 SessionMiddleware 仅为未来可扩展）
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# DRF + SimpleJWT
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "EXCEPTION_HANDLER": "core.exceptions.api_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPageNumberPagination",
    "PAGE_SIZE": 20,
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_MINUTES", default=30)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ---------------------------------------------------------------------------
# Django Channels（WebSocket 走 Redis Channel Layer）
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [env("REDIS_URL", default="redis://redis:6379/2")]},
    }
}

# ---------------------------------------------------------------------------
# Celery —— Redis Broker / Result Backend + Beat
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ---------------------------------------------------------------------------
# 健康检查与跨域
# ---------------------------------------------------------------------------
HEALTH_CHECK = {
    "REDIS_URL": env("REDIS_URL", default="redis://redis:6379/2"),
    "CELERY_TIMEOUT_SECONDS": 2,
}

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# 日志：Console + 滚动文件，每条记录前自动附带当前链路 request_id
# ---------------------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {"()": "core.logging_utils.RequestIDFilter"},
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [rid:%(request_id)s] %(levelname)s %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "encoding": "utf-8",
            "filters": ["request_id"],
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
        "apps": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
        "core": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
        "celery": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
    },
}
