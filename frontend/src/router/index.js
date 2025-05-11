import { createRouter, createWebHistory } from 'vue-router'

// 页面组件
const Login = () => import('../views/Login.vue')
const Dashboard = () => import('../views/Dashboard.vue')

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫，用于权限控制
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要登录但未登录，重定向到登录页
    next({ name: 'Login' })
  } else if (to.path === '/login' && token) {
    // 已登录状态访问登录页，重定向到控制台
    next({ name: 'Dashboard' })
  } else {
    // 正常导航
    next()
  }
})

export default router