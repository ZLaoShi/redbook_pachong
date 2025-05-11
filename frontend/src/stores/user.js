import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || '{}')
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    userProfile: (state) => state.user
  },
  
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/v1/login/access-token', new URLSearchParams({
          username,
          password
        }), {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
        
        const token = response.data.access_token
        
        // 保存 token 到 localStorage 和 state
        localStorage.setItem('token', token)
        this.token = token
        
        // 获取用户信息
        await this.getUserInfo()
        
        return { success: true }
      } catch (error) {
        console.error('Login failed:', error)
        return {
          success: false,
          message: error.response?.data?.detail || '登录失败，请检查用户名和密码'
        }
      }
    },
    
    async getUserInfo() {
      try {
        const response = await axios.get('/api/v1/users/me', {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        
        // 保存用户信息
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        
        return response.data
      } catch (error) {
        console.error('Failed to get user info:', error)
        return null
      }
    },
    
    logout() {
      // 清除 token 和用户信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.token = ''
      this.user = {}
    }
  }
})