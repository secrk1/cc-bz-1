<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  editing: { type: Object, default: null },
})

const emits = defineEmits(['update:visible', 'submit'])

const formRef = ref(null)
const defaultForm = () => ({
  name: '',
  code: '',
  env_type: 'dev',
  cluster_endpoint: 'https://',
  namespace: 'default',
  description: '',
  status: 'active',
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入环境标识', trigger: 'blur' },
    { pattern: /^[a-z0-9-]+$/, message: '仅允许小写字母、数字与连字符', trigger: 'blur' },
  ],
  env_type: [{ required: true, message: '请选择环境类型', trigger: 'change' }],
  cluster_endpoint: [{ required: true, type: 'url', message: '请输入合法的集群 API 地址', trigger: 'blur' }],
}

watch(
  () => props.visible,
  (visible) => {
    if (!visible) return
    Object.assign(form, props.editing ? { ...defaultForm(), ...props.editing } : defaultForm())
  },
)

const close = () => emits('update:visible', false)

const handleSubmit = async () => {
  await formRef.ref?.validate()
  emits('submit', { ...form })
  close()
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    :title="editing ? '编辑运行环境' : '新增运行环境'"
    width="560px"
    destroy-on-close
    @update:model-value="emits('update:visible', $event)"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="92px" class="pr-4">
      <el-form-item label="环境名称" prop="name">
        <el-input v-model="form.name" placeholder="如：生产集群-华东" />
      </el-form-item>
      <el-form-item label="环境标识" prop="code">
        <el-input v-model="form.code" placeholder="如：prod-k8s-east" :disabled="Boolean(editing)" />
      </el-form-item>
      <el-form-item label="环境类型" prop="env_type">
        <el-radio-group v-model="form.env_type">
          <el-radio-button value="dev">Dev</el-radio-button>
          <el-radio-button value="staging">Staging</el-radio-button>
          <el-radio-button value="prod">Prod</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="API 地址" prop="cluster_endpoint">
        <el-input v-model="form.cluster_endpoint" placeholder="https://k8s-api:6443" />
      </el-form-item>
      <el-form-item label="命名空间">
        <el-input v-model="form.namespace" placeholder="default" />
      </el-form-item>
      <el-form-item label="初始状态">
        <el-select v-model="form.status">
          <el-option label="可用" value="active" />
          <el-option label="维护中" value="maintaining" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="环境用途与变更注意事项" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>
