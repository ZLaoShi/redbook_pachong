<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { login } from '../api/user'

const router = useRouter()
const message = useMessage()

// 表单数据
const formData = reactive({
  username: '',
  password: ''
})

// 表单加载状态
const loading = ref(false)

// 登录处理
const handleLogin = async () => {
  // 简单表单验证
  if (!formData.username || !formData.password) {
    message.error('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const response = await login(formData)
    
    // 保存 token 到 localStorage
    localStorage.setItem('token', response.access_token)
    
    // 显示成功消息
    message.success('登录成功')
    
    // 跳转到工作台页面
    router.push('/dashboard')
  } catch (error) {
    message.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">小红书内容分析工具</h1>
      
      <div class="form-item">
        <label>用户名</label>
        <input 
          type="text" 
          v-model="formData.username" 
          placeholder="请输入用户名"
          @keyup.enter="handleLogin"
        />
      </div>
      
      <div class="form-item">
        <label>密码</label>
        <input 
          type="password" 
          v-model="formData.password" 
          placeholder="请输入密码"
          @keyup.enter="handleLogin"
        />
      </div>
      
      <button 
        class="login-button" 
        @click="handleLogin"
        :disabled="loading"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  
  .login-card {
    width: 400px;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    background-color: white;
    
    .login-title {
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
    
    .login-button {
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
  }
}
</style>