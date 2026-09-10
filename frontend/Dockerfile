# ---------- 构建阶段 ----------
FROM node:20-alpine AS builder

WORKDIR /app

# 优先利用 Docker 层缓存：依赖清单变更才重新安装
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- 托管阶段 ----------
FROM nginx:1.27-alpine

# 自定义站点配置：SPA 回退 + /api、/ws 反向代理
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# nginx:alpine 自带 busybox wget，探活 SPA 入口
HEALTHCHECK --interval=15s --timeout=5s --retries=5 --start-period=10s \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
