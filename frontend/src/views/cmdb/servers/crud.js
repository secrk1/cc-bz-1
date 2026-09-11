/**
 * 服务器资产 fast-crud 配置：列 / 搜索 / 表单 / 枚举字典。
 * 字段命名与后端 ServerSerializer 对齐，外键 environment 提交环境 id。
 */
import { dict } from '@fast-crud/fast-crud'

import { createCrudRequest } from '@/api/crud'

// 运行状态字典（带标签色，fast-crud 会自动渲染为 el-tag）
const statusDict = dict({
  data: [
    { value: 'running', label: '运行中', color: 'success' },
    { value: 'stopped', label: '已停机', color: 'info' },
    { value: 'maintaining', label: '维护中', color: 'warning' },
    { value: 'abnormal', label: '异常', color: 'danger' },
    { value: 'retired', label: '已下线', color: 'info' },
  ],
})

const providerDict = dict({
  data: [
    { value: 'vm', label: '虚拟机', color: 'primary' },
    { value: 'physical', label: '物理机', color: 'warning' },
    { value: 'cloud', label: '云主机', color: 'success' },
  ],
})

/**
 * @param environmentOptions 环境字典数据 [{ value, label }]，页面先拉取后注入，
 *        保证纳管表单的环境下拉立即可用（非远程懒加载，避免空下拉）。
 */
export function buildServerCrudOptions(environmentOptions = []) {
  const environmentDict = dict({ data: environmentOptions })
  return {
    // 注意：fast-crud 从 crudOptions.request.pageRequest 读取，request 必须是嵌套对象
    request: createCrudRequest('/cmdb/servers'),
    search: {
      show: true, // 开启顶部查询容器，字段是否可搜由各列 search.show 控制
      col: { span: 6 },
    },
    actionbar: {
      buttons: { add: { text: '纳管服务器' } },
    },
    rowHandle: {
      fixed: 'right',
      width: 170,
    },
    table: {
      border: true,
      stripe: true,
      // 表格自适应填满父容器（随窗口缩放、表头固定、表体内部滚动）
      height: 'auto',
    },
    columns: {
      hostname: {
        title: '主机名',
        type: 'text',
        column: { width: 170, fixed: 'left' },
        search: { show: true },
        form: {
          rules: [{ required: true, message: '请输入主机名' }],
          helper: '同一 CMDB 内唯一',
        },
      },
      ip_address: {
        title: '管理 IP',
        type: 'text',
        column: { width: 140 },
        search: { show: true, placeholder: 'IP 搜索' },
        form: {
          rules: [{ required: true, message: '请输入管理 IP' }],
          helper: 'IPv4 / IPv6',
        },
      },
      private_ip: {
        title: '内网 IP',
        type: 'text',
        column: { width: 140 },
      },
      environment: {
        title: '所属环境',
        type: 'dict-select',
        dict: environmentDict,
        column: { width: 160 },
        search: { show: true, width: 140 },
        form: {
          value: environmentOptions[0]?.value,
          rules: [{ required: true, message: '请选择所属环境' }],
        },
      },
      provider: {
        title: '主机类型',
        type: 'dict-select',
        dict: providerDict,
        column: { width: 100 },
        search: { show: true, width: 120 },
        form: { value: 'vm' },
      },
      status: {
        title: '运行状态',
        type: 'dict-select',
        dict: statusDict,
        column: { width: 100 },
        search: { show: true, width: 120 },
        form: { value: 'running' },
      },
      cpu_cores: {
        title: 'CPU(核)',
        type: 'number',
        column: { width: 90 },
        form: { value: 0, min: 0 },
      },
      memory_mb: {
        title: '内存(MB)',
        type: 'number',
        column: { width: 100 },
        form: { value: 0, min: 0 },
      },
      disk_gb: {
        title: '磁盘(GB)',
        type: 'number',
        column: { width: 100 },
        form: { value: 0, min: 0 },
      },
      spec: {
        title: '规格型号',
        type: 'text',
        column: { width: 130 },
        form: { show: { edit: true } },
      },
      os_name: {
        title: '操作系统',
        type: 'text',
        column: { width: 140 },
      },
      os_version: {
        title: '系统版本',
        type: 'text',
        column: { width: 110 },
      },
      region: {
        title: '机房/可用区',
        type: 'text',
        column: { width: 130 },
      },
      remark: {
        title: '备注',
        type: 'textarea',
        column: { show: false },
      },
      created_at: {
        title: '纳管时间',
        type: 'text',
        column: { width: 170 },
        form: { show: false },
        addForm: { show: false },
        editForm: { disabled: true },
      },
    },
  }
}
