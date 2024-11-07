<template>
  <div class="space-y-8">
    <!-- 基本信息表单 -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium">基本信息</h3>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">标题 *</label>
        <input 
          v-model="form.title" 
          class="w-full border rounded-md px-3 py-2" 
          placeholder="请输入文章标题"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">作者 *</label>
        <author-select v-model="form.author_id" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">内容 *</label>
        <textarea 
          v-model="form.content" 
          rows="6" 
          class="w-full border rounded-md px-3 py-2" 
          placeholder="请输入文章内容"
        ></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">标签</label>
        <div class="space-x-4">
          <label v-for="tag in ['24小时', '博客', '论文', '微信', '视频']" :key="tag" class="inline-flex items-center">
            <input 
              type="checkbox" 
              :value="tag" 
              v-model="form.tags" 
              class="rounded border-gray-300"
            />
            <span class="ml-2">{{ tag }}</span>
          </label>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">频道</label>
        <div class="space-x-4">
          <label v-for="channel in ['微信', 'YouTube', '小宇宙', 'PDF','视频']" :key="channel" class="inline-flex items-center">
            <input 
              type="radio" 
              :value="channel" 
              v-model="form.channel" 
              class="border-gray-300"
            />
            <span class="ml-2">{{ channel }}</span>
          </label>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">发布日期</label>
        <input 
          type="date" 
          v-model="form.publish_date" 
          class="w-full border rounded-md px-3 py-2"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">原文链接</label>
        <input 
          v-model="form.original_link" 
          class="w-full border rounded-md px-3 py-2" 
          placeholder="请输入原文链接"
        />
      </div>
    </div>

    <!-- 小节内容表单 -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium">小节内容</h3>
      <div v-for="sectionType in ALL_SECTION_TYPES" :key="sectionType" class="border rounded-lg p-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">{{ sectionType }}</label>
        <textarea 
          v-model="sections[sectionType]"
          rows="4"
          class="w-full border rounded-md px-3 py-2"
          :placeholder="`请输入${sectionType}内容（支持 Markdown 格式）`"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import AuthorSelect from './AuthorSelect.vue'
import type { Article } from '../types/article'
import type { ArticleSection, SectionType } from '../types/section'
import { ALL_SECTION_TYPES } from '../types/section'
import { supabase } from '../supabaseClient'

interface Props {
  modelValue: Partial<Article>;
  articleId?: number;
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 小节内容管理
const sections = ref<Record<SectionType, string>>({} as Record<SectionType, string>)
const expandedSections = ref<Set<SectionType>>(new Set(ALL_SECTION_TYPES))

// 添加自动保存定时器
let autoSaveTimerId: number | null = null

// 保存所有表单数据的方法
const saveFormData = () => {
  // 如果是编辑模式，不保存草稿
  if (props.articleId) {
    return
  }

  const formData = {
    basic: form.value,
    sections: sections.value
  }
  localStorage.setItem('articleFormDraft', JSON.stringify(formData))
}

// 恢复表单数据的方法
const restoreFormData = () => {
  // 如果是编辑模式（有 articleId），则不恢复草稿
  if (props.articleId) {
    return
  }

  const savedData = localStorage.getItem('articleFormDraft')
  if (savedData) {
    const parsedData = JSON.parse(savedData)
    // 恢复基本表单数据
    emit('update:modelValue', parsedData.basic)
    // 恢复小节内容
    if (parsedData.sections) {
      sections.value = parsedData.sections
    }
  }
}

// 清除草稿的方法
const clearDraft = () => {
  localStorage.removeItem('articleFormDraft')
  // 重置基本表单
  emit('update:modelValue', {})
  // 重置小节内容
  sections.value = {} as Record<SectionType, string>
}

// 设置自动保存
onMounted(() => {
  restoreFormData()
  autoSaveTimerId = window.setInterval(saveFormData, 30000) // 每30秒保存一次
})

// 清理定时器
onBeforeUnmount(() => {
  if (autoSaveTimerId) {
    clearInterval(autoSaveTimerId)
  }
})

// 监听表单和小节内容的变化
watch([form, sections], () => {
  saveFormData()
}, { deep: true })

// 监听 articleId 的变化
watch(() => props.articleId, async (newId) => {
  if (newId) {
    // 如果是编辑模式，清除草稿数据
    localStorage.removeItem('articleFormDraft')
    
    const { data, error } = await supabase
      .from('keep_article_sections')
      .select('*')
      .eq('article_id', newId)
      .order('sort_order', { ascending: true })

    if (!error && data) {
      // 清空之前的数据
      sections.value = {} as Record<SectionType, string>
      // 设置新数据
      data.forEach((section: any) => {
        if (section && 'section_type' in section && 'content' in section) {
          sections.value[section.section_type as SectionType] = section.content as string
        }
      })
    }
  }
}, { immediate: true }) // 添加 immediate: true 确保首次加载时也执行

// 获取要提交的小节数据
const getSectionsData = () => {
  return Object.entries(sections.value)
    .filter(([_, content]) => content.trim())
    .map(([type, content], index) => ({
      section_type: type as SectionType,
      content,
      sort_order: (index + 1) * 10
    }))
}

defineExpose({
  getSectionsData
})
</script> 

<style scoped>
</style> 