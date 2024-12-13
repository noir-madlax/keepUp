<template>
  <button
    class="flex items-center gap-1 px-2 py-1 text-gray-600 hover:text-gray-800"
    @click="toggleLanguage"
  >
    <img 
      :src="languageIcon"
      :alt="currentLanguage"
      class="w-6 h-6"
    />
  </button>
</template>

<script setup lang="ts">
// 导入所需的 Vue 组合式 API 和 vue-i18n
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

// 从 i18n 实例中获取 locale 对象
const { locale } = useI18n()

// 计算属性：获取当前语言
const currentLanguage = computed(() => locale.value)

// 计算属性：根据当前语言返回对应的图标路径
const languageIcon = computed(() => {
  return locale.value === 'zh' ? '/images/icons/CN.svg' : '/images/icons/EN.svg'
})

// 切换语言方法：在中文和英文之间切换
const toggleLanguage = () => {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
}
</script> 