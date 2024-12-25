<template>
  <div class="mermaid-container" :style="{ width: containerWidth, height: containerHeight }">
    <div ref="svgContainerRef" class="flex-1">
      <div v-if="renderError" class="error-container">
        <span class="error-text">Mermaid Syntax Error</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import mermaid from 'mermaid'
import { debounce } from 'lodash-es' // 需要安装 lodash-es

const props = defineProps<{
  content: string
}>()

const svgContainerRef = ref<HTMLElement | null>(null)
const renderError = ref(false)
let currentId = `mermaid-${Math.random().toString(36).substring(2)}`
let retryCount = 0
const MAX_RETRIES = 3

// 添加新的响应式变量
const containerHeight = ref('auto')
const containerWidth = ref('100%')

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
  },
  // 添加错误回调
  parseError: (err, hash) => {
    console.error('Mermaid parse error:', err)
    renderError.value = true
    return false // 阻止默认的错误处理
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

    // 修改节点识别的正则表达式，只匹配完整的节点ID（A、B、C、D、E、F等）
    const nodePattern = /\b([A-F])\b(?=\[)/g
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

// 使用防抖包装update函数
const debouncedUpdate = debounce(async () => {
  if (!svgContainerRef.value) return
  
  try {
    renderError.value = false
    const processedContent = transformer.transform(props.content)
    
    // 先进行语法解析检查
    try {
      await mermaid.parse(processedContent)
    } catch (parseError) {
      console.error('Mermaid 语法解析错误:', parseError)
      renderError.value = true
      return // 如果解析失败，直接返回不继续渲染
    }
    
    // 清空容器内容
    svgContainerRef.value.innerHTML = ''
    
    // 解析成功后进行渲染
    const { svg } = await mermaid.render(currentId, processedContent)
    
    // 检查返回的 SVG 是否包含错误标记
    if (svg.includes('syntax error') || 
        svg.includes('Parse error') || 
        svg.includes('mermaid-error')) {
      console.error('Mermaid 渲染结果包含错误')
      renderError.value = true
      return // 如果SVG包含错误标记，不进行渲染
    }
    
    // 确认无误后再更新容器内容
    svgContainerRef.value.innerHTML = svg
    
    // 获取生成的SVG元素并设置样式
    const svgElement = svgContainerRef.value.querySelector('svg')
    if (svgElement) {
      // 获取SVG的原始尺寸
      const bbox = svgElement.getBBox()
      const viewBox = svgElement.viewBox.baseVal
      
      // 计算宽高比
      const ratio = bbox.width / bbox.height
      
      // 获取可用空间 - 调整桌面端的计算逻辑
      const isMobile = window.innerWidth <= 768
      const availableWidth = isMobile 
        ? window.innerWidth * 0.9 
        : Math.min(window.innerWidth * 0.6, 800) // 降低最大宽度限制
      const availableHeight = isMobile
        ? window.innerHeight * 0.8
        : window.innerHeight * 0.6 // 桌面端高度占比调整
      
      // 根据宽高比和可用空间计算合适的容器尺寸
      if (ratio > 1) { // 宽大于高
        containerWidth.value = `${Math.min(availableWidth, bbox.width)}px`
        containerHeight.value = `${Math.min(availableWidth / ratio, availableHeight)}px`
      } else { // 高大于宽
        const calculatedHeight = Math.min(availableHeight, bbox.height)
        containerHeight.value = `${calculatedHeight}px`
        containerWidth.value = `${Math.min(calculatedHeight * ratio, availableWidth)}px`
      }
      
      // 设置SVG样式
      svgElement.style.width = '100%'
      svgElement.style.height = '100%'
      svgElement.setAttribute('preserveAspectRatio', 'xMidYMid meet')
    }
    
    retryCount = 0
    
  } catch (error) {
    console.error('Mermaid 渲染错误:', error)
    renderError.value = true
    
    if (retryCount < MAX_RETRIES) {
      retryCount++
      setTimeout(() => debouncedUpdate(), 1000 * retryCount)
    }
  }
}, 300)

// 手动重试方法
const retryRender = () => {
  retryCount = 0 // 重置重试计数
  debouncedUpdate()
}

onMounted(async () => {
  await debouncedUpdate()
  window.addEventListener('resize', debouncedUpdate)
})

watch(() => props.content, async () => {
  currentId = `mermaid-${Math.random().toString(36).substring(2)}`
  await debouncedUpdate()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', debouncedUpdate)
  debouncedUpdate.cancel() // 取消未执行的防抖函数
})
</script>

<style scoped>
.mermaid-container {
  min-width: unset;
  min-height: 200px;
  max-width: 100%;
  max-height: 80vh;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  margin: 0 auto;
  transition: all 0.3s ease;
}

/* 添加响应式样式 */
@media screen and (max-width: 768px) {
  .mermaid-container {
    min-width: unset;
    min-height: 200px;
    padding: 5px;
  }
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

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 100%;
}

.error-text {
  color: #666;
  font-size: 14px;
}
</style>