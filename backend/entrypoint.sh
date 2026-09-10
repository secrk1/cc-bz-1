#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# 容器启动前置：等待 PostgreSQL 就绪 -> 迁移 -> 收集静态文件 -> 拉起主进程
# 不同服务（web/daphne/celery）复用同一镜像，仅 web 执行迁移，靠 ROLE 区分。
# ---------------------------------------------------------------------------

ROLE="${CONTAINER_ROLE:-web}"

wait_for_postgres() {
  echo "[entrypoint] waiting for postgres ..."
  python - <<'PY'
import os
import time

import psycopg

url = os.environ.get("DATABASE_URL", "postgres://devops:devops@postgres:5432/devops_platform")
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with psycopg.connect(url, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        print("[entrypoint] postgres is ready")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"[entrypoint] postgres not ready: {exc}")
        time.sleep(2)
else:
    raise SystemExit("[entrypoint] postgres unavailable after 60s")
PY
}

if [[ "${ROLE}" == "web" || "${ROLE}" == "migrate" ]]; then
  wait_for_postgres
  echo "[entrypoint] applying migrations ..."
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput || true

  # 首次启动自动创建管理员（仅当 DJANGO_SUPERUSER_* 已提供），不依赖 Admin 站点
  python manage.py shell <<'PY' || true
import os

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email="")
    print(f"[entrypoint] superuser {username} created")
PY

  if [[ "${ROLE}" == "migrate" ]]; then
    exit 0
  fi
fi

echo "[entrypoint] starting: $*"
exec "$@"
