import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// fast-crud（基于 Element Plus 适配层）
import { FastCrud } from '@fast-crud/fast-crud'
import '@fast-crud/fast-crud/dist/style.css'
import FsElementPlus from '@fast-crud/ui-element'

import App from './App.vue'
import router from './router'

import http from './api/http'

import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './style.css'

const app = createApp(App)

// 全站启用 Element Plus 暗色主题变量（与平台深色框架统一，el-table/表单/弹窗/分页一致）
document.documentElement.classList.add('dark')

// 全局注册 Element Plus 图标
for (const [name, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(name, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 先安装 UI 适配层，再安装 fast-crud 核心
app.use(FsElementPlus)
app.use(FastCrud, {
  // 远程字典统一走平台 axios（响应拦截器已解包统一信封，返回 data）
  async dictRequest({ dict }) {
    return await http.get(dict.url, dict.http || {})
  },
})

app.mount('#app')
