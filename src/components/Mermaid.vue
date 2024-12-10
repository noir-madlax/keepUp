<template>
  <div class="mermaid-container">
    <div ref="mermaidRef" class="mermaid-content"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{
  content: string
}>()

const mermaidRef = ref<HTMLElement | null>(null)

// 处理 Mermaid 内容格式
const formatMermaidContent = (content: string) => {
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

  // 修改这部分的处理逻辑
  formattedContent = formattedContent
    .replace(/```mermaid/g, '')  // 移除可能存在的 mermaid 标记
    .replace(/```/g, '')         // 移除可能存在的代码块标记
    .trim()                      // 清理空白
    + '\n' + styles              // 添加样式

  return formattedContent
    .replace(/\\n/g, '\n')       // 处理换行符
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .trim()
}

// 修改 mermaid 配置
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  flowchart: {
    htmlLabels: true,
    curve: 'basis',
    rankSpacing: 40,     // 增加垂直间距
    nodeSpacing: 40,     // 增加水平间距
    padding: 10,         // 适当的内边距
    useMaxWidth: true,
    diagramPadding: 10   // 适当的图表边距
  }
})

// 修改自适应大小的处理函数
const adjustSvgSize = () => {
  if (!mermaidRef.value) return
  
  const svg = mermaidRef.value.querySelector('svg')
  if (!svg) return
  
  const container = mermaidRef.value.parentElement
  if (!container) return
  
  // 设置固定的容器高度（根据视口高度）
  container.style.height = '50vh'  // 减小为视口高度的50%
  
  // 获取容器尺寸
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  // 获取 SVG 原始尺寸
  const svgWidth = parseFloat(svg.getAttribute('width') || '0')
  const svgHeight = parseFloat(svg.getAttribute('height') || '0')
  
  // 计算缩放比例，确保完全适应容器
  const scaleX = (containerWidth / svgWidth) * 0.10  // 留出15%边距
  const scaleY = (containerHeight / svgHeight) * 0.10
  const scale = Math.min(scaleX, scaleY)
  
  // 应用缩放和居中
  svg.style.transform = `scale(${scale})`
  svg.style.transformOrigin = 'center'
}

const renderDiagram = async () => {
  if (!mermaidRef.value) return
  
  try {
    const formattedContent = formatMermaidContent(props.content)
    mermaidRef.value.innerHTML = formattedContent
    await mermaid.run({
      nodes: [mermaidRef.value]
    })
    // 渲染完成后调整大小
    adjustSvgSize()
  } catch (error) {
    console.error('Mermaid 渲染错误:', error)
    if (mermaidRef.value) {
      mermaidRef.value.innerHTML = `<pre style="color: red;">图表渲染失败，请检查语法\n${error}</pre>`
    }
  }
}

onMounted(() => {
  renderDiagram()
})

// 监听内容变化重新渲染
watch(() => props.content, () => {
  renderDiagram()
})

// 监听窗口大小变化
const handleResize = () => {
  renderDiagram()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.mermaid-container {
  width: 100%;
  height: 50vh;         /* 减小容器高度 */
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  margin: 1rem 0;
  padding: 0.5rem;      /* 减小内边距 */
}

.mermaid-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(svg) {
  max-width: 100% !important;
  max-height: 100% !important;
  width: auto !important;     /* 改为自动宽度 */
  height: auto !important;    /* 改为自动高度 */
  position: relative;
  transition: transform 0.3s ease;
}

/* 调整节点和文字大小 */
:deep(.node rect) {
  stroke-width: 1.5px;
}

:deep(.node text) {
  font-size: 14px;      /* 增大文字大小 */
}

:deep(.edgeLabel text) {
  font-size: 12px;      /* 增大连线文字大小 */
}

:deep(.node) {
  cursor: pointer;
}

:deep(.node rect) {
  stroke-width: 2px;
}

:deep(.node text) {
  font-size: 14px;
  fill: currentColor !important;
}

:deep(.edgePath path) {
  stroke-width: 2px;
  stroke: #666 !important;
}

/* 完全重写连线文字样式 */
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

/* 添加全局样式覆盖 */
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

:deep(.node:hover rect) {
  fill: inherit;
}
</style> 