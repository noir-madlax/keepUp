<template>
  <div class="space-y-4">
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
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue'
import AuthorSelect from './AuthorSelect.vue'
import type { Article } from '../types/article'

const props = defineProps<{
  modelValue: Partial<Article>
}>()

const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (value: Partial<Article>) => emit('update:modelValue', value)
})
</script> 