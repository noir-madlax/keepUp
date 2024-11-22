import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

// 导入 tailwind 基础样式
import './assets/tailwind.css'
// 导入 markdown 样式
import './assets/markdown.css'
// 导入 element-plus 样式
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
