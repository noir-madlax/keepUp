<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <label class="block text-sm font-medium text-gray-700">选择作者</label>
      <button 
        @click="showNewAuthorForm = true"
        class="text-sm text-blue-500 hover:text-blue-600"
      >
        创建新作者
      </button>
    </div>
    
    <select 
      v-model="selectedAuthorId"
      class="w-full border rounded-md px-3 py-2"
      @change="$emit('update:modelValue', selectedAuthorId)"
    >
      <option value="">请选择作者</option>
      <option 
        v-for="author in authors" 
        :key="author.id" 
        :value="author.id"
      >
        {{ author.name }}
      </option>
    </select>

    <!-- 创建新作者表单 -->
    <div v-if="showNewAuthorForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg w-[400px]" @click.stop>
        <h3 class="text-lg font-medium mb-4">创建新作者</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">作者名称</label>
            <input 
              v-model="newAuthor.name"
              class="w-full border rounded-md px-3 py-2"
              placeholder="请输入作者名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">作者图标</label>
            <input 
              v-model="newAuthor.icon"
              class="w-full border rounded-md px-3 py-2"
              placeholder="请输入图标链接"
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button 
              @click="showNewAuthorForm = false"
              class="px-4 py-2 border rounded-md hover:bg-gray-50"
            >
              取消
            </button>
            <button 
              @click="createAuthor"
              class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              创建
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { supabase } from '../supabaseClient'
import type { Author } from '../types/author'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
}>()

const authors = ref<Author[]>([])
const selectedAuthorId = ref<number | null>(props.modelValue)
const showNewAuthorForm = ref(false)
const newAuthor = ref({
  name: '',
  icon: ''
})

const fetchAuthors = async () => {
  try {
    const { data, error } = await supabase
      .from('keep_authors')
      .select('*')
      .order('name')
    
    if (error) throw error
    authors.value = data
  } catch (error) {
    console.error('获取作者列表失败:', error)
    ElMessage.error('获取作者列表失败')
  }
}

const createAuthor = async () => {
  try {
    if (!newAuthor.value.name) {
      ElMessage.warning('请输入作者名称')
      return
    }

    const { data, error } = await supabase
      .from('keep_authors')
      .insert([newAuthor.value])
      .select()
      .single()

    if (error) throw error

    authors.value.push(data)
    selectedAuthorId.value = data.id
    emit('update:modelValue', data.id)
    showNewAuthorForm.value = false
    newAuthor.value = { name: '', icon: '' }
    ElMessage.success('作者创建成功')
  } catch (error) {
    console.error('创建作者失败:', error)
    ElMessage.error('创建作者失败')
  }
}

onMounted(() => {
  fetchAuthors()
})
</script> 