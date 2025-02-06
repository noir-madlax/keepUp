import { createI18n } from 'vue-i18n'
import en from '../locales/en'
import zh from '../locales/zh'

// 获取浏览器语言设置
const getBrowserLanguage = () => {
  const language = navigator.language.toLowerCase()
  // 如果浏览器语言以 zh 开头（如 zh-CN, zh-TW 等），返回 zh，否则返回 en
  return language.startsWith('zh') ? 'zh' : 'en'
}

const i18n = createI18n({
  legacy: false,
 //locale: getBrowserLanguage(), // 使用浏览器语言作为初始语言
  locale: 'en', // 强制使用英文
  fallbackLocale: 'en',
  messages: {
    en,
    zh
  }
})

export default i18n 