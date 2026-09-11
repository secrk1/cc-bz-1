/**
 * fast-crud 请求工厂：把平台统一信封/分页适配为 fast-crud 的四个请求钩子。
 *
 * 约定（后端 core/responses.py + core/pagination.py）：
 * - 列表 GET `${base}`，查询参数 page / page_size，搜索字段以列名直传；
 * - 响应 data 形如 { items, total, page, page_size, total_pages }；
 * - 新增 POST `${base}`（201）、更新 PATCH `${base}/:id`、删除 DELETE `${base}/:id`。
 * axios 响应拦截器已解包信封，这里拿到的即后端 data。
 */
import http from './http'

// 剔除搜索表单中的空值，避免把空串 / undefined 发到后端
const cleanParams = (form = {}) =>
  Object.fromEntries(
    Object.entries(form).filter(
      ([, v]) => v !== '' && v !== null && v !== undefined,
    ),
  )

export function createCrudRequest(base) {
  return {
    // 分页查询 -> fast-crud 需要的 UserPageRes
    pageRequest: async (query) => {
      const { currentPage = 1, pageSize = 20 } = query.page || {}
      const data = await http.get(base, {
        params: { page: currentPage, page_size: pageSize, ...cleanParams(query.form) },
      })
      return {
        records: data.items || [],
        currentPage: data.page ?? currentPage,
        pageSize: data.page_size ?? pageSize,
        total: data.total ?? 0,
      }
    },
    addRequest: async ({ form }) => http.post(base, form),
    editRequest: async ({ form, row }) => http.patch(`${base}/${row.id}`, form),
    delRequest: async ({ row }) => http.delete(`${base}/${row.id}`),
  }
}
