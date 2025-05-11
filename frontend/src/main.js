import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import './style.css'

const app = createApp(App)

// 使用 Pinia 和 Vue Router
app.use(pinia)
app.use(router)

// 挂载应用
app.mount('#app')
