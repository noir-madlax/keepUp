<template>
  <div class="mind-map-container">
    <svg ref="container"></svg>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'
import type { IMarkmapOptions } from 'markmap-view'

const props = defineProps<{
  content: string
}>()

const container = ref<SVGElement | null>(null)
let markmap: any = null
const transformer = new Transformer()

// 创建或更新思维导图
const createOrUpdateMindMap = () => {
  if (!container.value) return
  
  const { root } = transformer.transform(props.content)
  
  if (!markmap) {
    const options: IMarkmapOptions = {
      autoFit: true,
      duration: 500,
      maxWidth: 300,
      initialExpandLevel: 2,
      color: (_, index) => {
        const colors = ['#2196F3', '#4CAF50', '#FFC107', '#E91E63', '#9C27B0']
        return colors[index % colors.length]
      },
      nodeMinHeight: 16,
      spacingHorizontal: 80,
      spacingVertical: 5,
      paddingX: 16,
    }
    
    markmap = Markmap.create(container.value, options)
  }
  
  markmap.setData(root)
  markmap.fit()
}

// 监听内容变化
watch(() => props.content, () => {
  createOrUpdateMindMap()
})

// 组件挂载时初始化
onMounted(() => {
  createOrUpdateMindMap()
  
  // 监听窗口大小变化，自动调整思维导图大小
  window.addEventListener('resize', createOrUpdateMindMap)
})

// 组件卸载时清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', createOrUpdateMindMap)
  markmap = null
})
</script>

<style scoped>
.mind-map-container {
  width: 100%;
  height: 600px;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

svg {
  width: 100%;
  height: 100%;
}

:deep(.markmap-node) {
  cursor: pointer;
}

:deep(.markmap-node-circle) {
  fill: #fff;
  stroke-width: 1.5;
}

:deep(.markmap-node-text) {
  fill: #333;
  font-family: Arial, sans-serif;
}

:deep(.markmap-link) {
  stroke: #999;
  stroke-width: 1.5;
}

:deep(.markmap-node:hover .markmap-node-circle) {
  fill: #f0f0f0;
}
</style>