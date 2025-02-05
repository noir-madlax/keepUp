<template>
  <div class="relative" :class="containerClass">
    <input
      type="text"
      v-model="localUrl"
      :placeholder="'Place any Video/Podcast link here to summarize'"
      :class="[inputClass, { 'input-highlight': isHighlighted }]"
      @keyup.enter="handleNewUploadClick('url')"
      @focus="handleInputFocus"
      @blur="handleInputBlur"
    />
    <img 
      src="/images/icons/enter.svg" 
      alt="Press Enter" 
      :class="enterIconClass"
      @click="handleNewUploadClick('url')"
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

// 处理函数
const handleInputFocus = async () => {
  isHighlighted.value = true
  if (!('ontouchstart' in window)) {
    await handlePaste()
  }
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

const handleNewUploadClick = (type: 'url') => {
  if (!authStore.isAuthenticated) {
    emit('showLogin')
    return
  }

  if (type === 'url' && localUrl.value) {
    if (localUrl.value.startsWith('http://') || localUrl.value.startsWith('https://')) {
      emit('submit', localUrl.value)
    }
  }
}

defineExpose({
  handleNewUploadClick
})
</script> 