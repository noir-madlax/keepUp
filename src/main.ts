import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 导入 tailwind 基础样式
import './assets/tailwind.css'
// 导入 markdown 样式
import './assets/markdown.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
