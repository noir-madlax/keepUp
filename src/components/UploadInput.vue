<template>
  <div class="relative" :class="containerClass">
    <input
      type="text"
      v-model="localUrl"
      :placeholder="'Paste YouTube/Podcasts link here'"
      :class="[inputClass, { 'input-highlight': isHighlighted }]"
      @keyup.enter="handleNewUploadClick('url')"
      @focus="handleInputFocus"
      @blur="handleInputBlur"
      @touchend.prevent="handleTouchEnd"
    />
    <img 
      src="/images/icons/enter.svg" 
      alt="Press Enter" 
      :class="[enterIconClass, 'cursor-pointer touch-manipulation']"
      @click="handleNewUploadClick('url')"
      @touchend.prevent="handleNewUploadClick('url')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{
  modelValue: string
  containerClass?: string
  inputClass?: string
  enterIconClass?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'submit': [url: string]
  'showLogin': []
}>()

const authStore = useAuthStore()
const isHighlighted = ref(false)
const localUrl = ref(props.modelValue)

// 双向绑定
watch(() => props.modelValue, (newVal) => {
  localUrl.value = newVal
})

watch(localUrl, (newVal) => {
  emit('update:modelValue', newVal)
})

// 处理移动端触摸结束事件
const handleTouchEnd = (event: TouchEvent) => {
  // 防止触发其他事件
  event.preventDefault()
  // 聚焦输入框
  const input = event.target as HTMLInputElement
  input.focus()
}

// 处理函数
const handleInputFocus = async () => {
  isHighlighted.value = true
  // 移除设备类型判断，在所有设备上尝试粘贴
  await handlePaste()
}

const handleInputBlur = () => {
  isHighlighted.value = false
}

const handlePaste = async () => {
  try {
    if (!navigator.clipboard) return
    const text = await navigator.clipboard.readText()
    if (text.includes('http') && text.includes('.')) {
      localUrl.value = text.trim()
    }
  } catch (err) {
    console.error('Failed to read clipboard:', err)
  }
}

const handleNewUploadClick = async (type: 'url') => {
  if (!authStore.isAuthenticated) {
    emit('showLogin')
    return
  }

  if (type === 'url') {
    if (!localUrl.value) {
      // 2024-03-25: 如果URL为空，尝试读取剪贴板
      await handlePaste()
    } else if (localUrl.value.startsWith('http://') || localUrl.value.startsWith('https://')) {
      emit('submit', localUrl.value)
    }
  }
}

defineExpose({
  handleNewUploadClick
})
</script>

<style scoped>
/* 增加移动端的交互体验 */
input {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 确保点击区域足够大 */
img {
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
}

/* 禁用移动端的双击缩放 */
* {
  touch-action: manipulation;
}
</style> 