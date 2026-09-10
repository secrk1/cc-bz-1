<script setup>
import DomainHome from '@/components/domain/DomainHome.vue'

const metrics = [
  { label: '登录账号', value: 24, suffix: '人', trend: '启用 MFA 18 人', icon: 'User', tone: 'cyan' },
  { label: '角色', value: 6, suffix: '个', trend: '最小权限模型', icon: 'UserFilled', tone: 'indigo' },
  { label: '通知渠道', value: 3, suffix: '个', trend: '钉钉 / 企微 / 邮件', icon: 'Bell', tone: 'emerald' },
  { label: '审计日志', value: 9.8, suffix: '万条', trend: '保留 180 天', icon: 'Notebook', tone: 'amber' },
]

const entries = [
  { title: '用户与权限', desc: '账号、角色与菜单权限配置（待接入）', icon: 'Lock', accent: 'cyan' },
  { title: '通知渠道', desc: '告警与发布通知的 Webhook 配置（待接入）', icon: 'Bell', accent: 'indigo' },
  { title: '令牌管理', desc: 'API Token 与密钥轮换（待接入）', icon: 'Key', accent: 'amber' },
  { title: '系统参数', desc: '平台级开关与默认值配置（待接入）', icon: 'Setting', accent: 'emerald' },
]
</script>

<template>
  <DomainHome
    title="系统设置"
    description="账号权限、通知集成与平台级参数配置"
    :metrics="metrics"
    :entries="entries"
  />
</template>
