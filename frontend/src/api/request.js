import axios from 'axios'
import router from '../router'
import config from '../config'

// 根据环境选择基础URL
const baseURL = import.meta.env.PROD ? config.prod.baseURL : config.dev.baseURL

const service = axios.create({
  baseURL,
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const { status, data } = error.response || {}
    
    // 处理401未授权错误
    if (status === 401) {
      // 清除本地token
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 跳转到登录页
      router.push('/login')
      
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }
    
    // 处理其他错误
    const errorMsg = data?.detail || '服务器错误，请稍后重试'
    console.error('响应错误:', errorMsg)
    
    return Promise.reject(new Error(errorMsg))
  }
)

export default service