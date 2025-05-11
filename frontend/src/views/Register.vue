<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { register } from '../api/user' // 确保你已经创建了 register API 函数

const router = useRouter()
const message = useMessage()

// 表单数据
const formData = reactive({
  username: '',
  email: '', // 添加 email 字段
  password: ''
})

// 表单加载状态
const loading = ref(false)

// 注册处理
const handleRegister = async () => {
  // 简单表单验证
  if (!formData.username || !formData.password || !formData.email) {
    message.error('请输入用户名、邮箱和密码')
    return
  }
  // 简单的邮箱格式验证
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailPattern.test(formData.email)) {
    message.error('请输入有效的邮箱地址')
    return
  }

  loading.value = true
  try {
    await register(formData) // 调用注册 API
    message.success('注册成功！请登录。')
    router.push('/login') // 注册成功后跳转到登录页面
  } catch (error) {
    message.error(error.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="register-title">创建新账户</h1>

      <div class="form-item">
        <label>用户名</label>
        <input
          type="text"
          v-model="formData.username"
          placeholder="请输入用户名"
          @keyup.enter="handleRegister"
        />
      </div>

      <div class="form-item">
        <label>邮箱</label>
        <input
          type="email"
          v-model="formData.email"
          placeholder="请输入邮箱"
          @keyup.enter="handleRegister"
        />
      </div>

      <div class="form-item">
        <label>密码</label>
        <input
          type="password"
          v-model="formData.password"
          placeholder="请输入密码"
          @keyup.enter="handleRegister"
        />
      </div>

      <button
        class="register-button"
        @click="handleRegister"
        :disabled="loading"
      >
        {{ loading ? '注册中...' : '注册' }}
      </button>

      <div class="login-link">
        已有账户？ <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;

  .register-card {
    width: 400px;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    background-color: white;

    .register-title {
      text-align: center;
      margin-bottom: 30px;
      color: #333;
      font-size: 24px;
    }

    .form-item {
      margin-bottom: 20px;

      label {
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
        color: #333;
      }

      input {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;

        &:focus {
          outline: none;
          border-color: #18a058;
        }
      }
    }

    .register-button {
      width: 100%;
      padding: 12px;
      background-color: #18a058;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 16px;
      cursor: pointer;
      transition: background-color 0.3s;

      &:hover {
        background-color: #0c7a43;
      }

      &:disabled {
        background-color: #a8e2c0;
        cursor: not-allowed;
      }
    }
    .login-link {
      margin-top: 20px;
      text-align: center;
      font-size: 14px;
      color: #666;

      a {
        color: #18a058;
        text-decoration: none;
        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}
</style>