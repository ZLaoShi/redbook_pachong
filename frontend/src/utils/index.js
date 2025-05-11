import axios from 'axios'
import { useUserStore } from '../stores/user'

// 创建 axios 实例
const instance = axios.create({
  baseURL: '/api', // API 基础 URL
  timeout: 30000 // 请求超时时间
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 处理 401 Unauthorized 错误
    if (error.response && error.response.status === 401) {
      // 获取用户 store 并执行登出
      const userStore = useUserStore()
      userStore.logout()
      
      // 重定向到登录页面
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default instance