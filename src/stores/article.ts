import { defineStore } from 'pinia'
import { ref } from 'vue'
import { SectionType, DEFAULT_SELECTED_SECTIONS } from '../types/section'

export const useArticleStore = defineStore('article', () => {
  // 当前显示的小节类型列表
  const selectedSections = ref<SectionType[]>([...DEFAULT_SELECTED_SECTIONS])

  return {
    selectedSections
  }
}) 