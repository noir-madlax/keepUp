<template>
  <div class="mermaid-container flex">
    <div ref="svgContainerRef" class="flex-1"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{
  content: string
}>()

const svgContainerRef = ref<HTMLElement | null>(null)
let currentId = `mermaid-${Math.random().toString(36).substring(2)}`

// 初始化mermaid配置
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  flowchart: {
    htmlLabels: true,
    curve: 'basis',
    rankSpacing: 40,
    nodeSpacing: 40,
    padding: 10,
    useMaxWidth: false,
    diagramPadding: 10
  }
})

// 数据转换器
const transformer = {
  transform(content: string) {
    let formattedContent = content.trim()
    
    // 定义颜色映射
    const colors = {
      color1: '#2874A6',
      color2: '#517C34',
      color3: '#C0392B',
      color4: '#D35400',
    color5: '#8E44AD',
    color6: '#34495E',
    color7: '#1ABC9C',
    color8: '#2ECC71',
    color9: '#27AE60',
    color10: '#2ECC71'

    }

    // 查找所有节点ID
    const nodePattern = /\b([A-Za-z][A-Za-z0-9]*)\b\s*[\[\("\{]/g
    const nodes = new Set<string>()
    let match
    
    while ((match = nodePattern.exec(formattedContent)) !== null) {
      nodes.add(match[1])
    }

    // 生成样式定义
    const styles = Array.from(nodes).map((node, index) => {
      const colorKey = `color${(index % 4) + 1}` as keyof typeof colors
      const color = colors[colorKey]
      return `style ${node} fill:${color},stroke:${color},color:#fff`
    }).join('\n')

    return formattedContent
      .replace(/```mermaid/g, '')
      .replace(/```/g, '')
      .replace(/\\n/g, '\n')
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      .trim() + '\n' + styles
  }
}

// 更新函数
const update = async () => {
  if (!svgContainerRef.value) return
  
  try {
    const processedContent = transformer.transform(props.content)
    
    // 使用 mermaid.render 获取 SVG
    const { svg } = await mermaid.render(currentId, processedContent)
    
    // 更新容器内容
    svgContainerRef.value.innerHTML = svg
    
    // 获取生成的SVG元素并设置样式
    const svgElement = svgContainerRef.value.querySelector('svg')
    if (svgElement) {
      svgElement.style.width = '100%'
      svgElement.style.height = '100%'
      // 确保SVG响应式
      svgElement.setAttribute('preserveAspectRatio', 'xMidYMid meet')
    }
  } catch (error) {
    console.error('Mermaid 渲染错误:', error)
    if (svgContainerRef.value) {
      svgContainerRef.value.innerHTML = `<pre style="color: red;">图表渲染失败: ${error}</pre>`
    }
  }
}

onMounted(async () => {
  await update()
  window.addEventListener('resize', update)
})

watch(() => props.content, async () => {
  // 每次更新时生成新的ID，避免缓存问题
  currentId = `mermaid-${Math.random().toString(36).substring(2)}`
  await update()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', update)
})
</script>

<style scoped>
.mermaid-container {
  width: 100%;
  height: 720px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.flex-1 {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(svg) {
  max-width: 90%;
  max-height: 90%;
  margin: auto;
}

:deep(.node) {
  cursor: pointer;
}

:deep(.node rect) {
  stroke-width: 2px;
}

:deep(.node text) {
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  fill: currentColor !important;
}

:deep(.edgePath path) {
  stroke: #666 !important;
  stroke-width: 2px;
}

:deep(.edgeLabel) {
  background-color: transparent !important;
  color: #333;
}

:deep(.edgeLabel *) {
  background-color: transparent !important;
  background: transparent !important;
}

:deep(.edgeLabel div) {
  background-color: transparent !important;
  background: transparent !important;
}

:deep(.edgeLabel span) {
  background-color: transparent !important;
  background: transparent !important;
}

:deep(.edgeLabel foreignObject) {
  background-color: transparent !important;
  background: transparent !important;
}

:deep(.edgeLabel rect) {
  opacity: 0 !important;
  fill: none !important;
  stroke: none !important;
  display: none !important;  /* 完全隐藏背景矩形 */
}

:deep(.node:hover rect) {
  fill: #f8f8f8;
}

/* 全局样式覆盖 */
:deep([id^="L-"]) {
  background-color: transparent !important;
  background: transparent !important;
}

:deep([id^="L-"] *) {
  background-color: transparent !important;
  background: transparent !important;
}

/* 确保SVG内所有可能的背景都被移除 */
:deep(svg *[fill="#ffffff"]) {
  fill: transparent !important;
}

:deep(svg *[fill="#fff"]) {
  fill: transparent !important;
}
</style>