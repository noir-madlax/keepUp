<template>
  <div class="mind-map-container" :style="{ width: containerWidth, height: containerHeight }">
    <div ref="svgContainerRef" class="flex-1">
      <div v-if="renderError" class="error-container">
        <span class="error-text">思维导图加载失败</span>
        <el-button type="primary" size="small" @click="retryRender">
          重试
        </el-button>
      </div>
      <svg ref="svgRef" v-show="!renderError" class="flex-1" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'
import { debounce } from 'lodash-es'

const props = defineProps<{
  content: string
}>()

const emit = defineEmits<{
  (e: 'preview', url: string): void
}>()

const svgRef = ref<SVGElement | null>(null)
const svgContainerRef = ref<HTMLElement | null>(null)
const renderError = ref(false)
const containerWidth = ref('100%')
const containerHeight = ref('auto')
let mm: any = null
const transformer = new Transformer()
let retryCount = 0
const MAX_RETRIES = 3
const isRendered = ref(false)

const debouncedUpdate = debounce(async () => {
  if (!svgRef.value || !mm) return
  
  try {
    renderError.value = false
    const { root } = transformer.transform(props.content)
    mm.setData(root)
    
    // 先执行一次fit以获取正确的内容尺寸
    mm.fit()
    
    const svgElement = svgRef.value
    if (svgElement) {
      // 获取SVG的实际尺寸
      const bbox = svgElement.getBBox()
      const viewBox = svgElement.viewBox.baseVal
      
      // 计算宽高比
      const ratio = bbox.width / bbox.height
      
      // 获取可用空间
      const isMobile = window.innerWidth <= 768
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      
      // 修改可用空间计算逻辑
      const availableWidth = isMobile 
        ? viewportWidth * 0.9 
        : Math.min(viewportWidth * 0.6, 800) // 降低最大宽度限制
      const availableHeight = isMobile
        ? viewportHeight * 0.8
        : viewportHeight * 0.6 // 调整桌面端高度占比
      
      // 根据宽高比和可用空间计算合适的容器尺寸
      if (ratio > 1.2) { // 横向内容较多
        containerWidth.value = `${Math.min(availableWidth, bbox.width)}px`
        containerHeight.value = `${Math.min(availableWidth / ratio, availableHeight)}px`
      } else if (ratio < 0.8) { // 纵向内容较多
        const calculatedHeight = Math.min(availableHeight, bbox.height)
        containerHeight.value = `${calculatedHeight}px`
        containerWidth.value = `${Math.min(calculatedHeight * ratio, availableWidth)}px`
      } else { // 近似正方形内容
        const size = Math.min(availableWidth, availableHeight)
        containerWidth.value = `${size}px`
        containerHeight.value = `${size}px`
      }
      
      // 设置SVG样式
      svgElement.style.width = '100%'
      svgElement.style.height = '100%'
      svgElement.setAttribute('preserveAspectRatio', 'xMidYMid meet')
      
      // 最后再次fit确保内容正确显示
      setTimeout(() => {
        mm.fit()
        // 在这里设置渲染完成标志
        isRendered.value = true
      }, 1000)
    }
    
    retryCount = 0
    
  } catch (error) {
    console.error('MindMap 渲染错误:', error)
    renderError.value = true
    
    if (retryCount < MAX_RETRIES) {
      retryCount++
      setTimeout(() => debouncedUpdate(), 1000 * retryCount)
    }
  }
}, 300)

const retryRender = () => {
  retryCount = 0
  if (!svgRef.value) return
  
  try {
    mm = Markmap.create(svgRef.value, {
      duration: 0,
      pan: false,
      zoom: false,
    })
    debouncedUpdate()
  } catch (error) {
    console.error('MindMap 初始化错误:', error)
    renderError.value = true
  }
}

const exportAsPng = (needDownload = false) => {
  if (!svgRef.value || !isRendered.value) return
  
  // 获取当前SVG的克隆副本，以确保获取完整内容
  const clonedSvg = svgRef.value.cloneNode(true) as SVGElement
  
  // 获取SVG的实际尺寸
  const bbox = svgRef.value.getBBox()
  
  // 设置明确的宽高和viewBox以确保完整捕获
  clonedSvg.setAttribute('width', bbox.width.toString())
  clonedSvg.setAttribute('height', bbox.height.toString())
  clonedSvg.setAttribute('viewBox', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`)
  
  // 获取完整的SVG字符串
  const svgString = new XMLSerializer().serializeToString(clonedSvg)
  const svgUrl = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgString)))}`
  
  // 创建Image对象
  const img = new Image()
  img.onload = () => {
    // 创建canvas，使用8倍缩放比例
    const canvas = document.createElement('canvas')
    const scale = 8 // 增加到8倍分辨率
    canvas.width = bbox.width * scale
    canvas.height = bbox.height * scale
    
    // 绘制到canvas
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // 设置更好的图像质量
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'
    
    // 设置白色背景
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // 缩放并绘制
    ctx.scale(scale, scale)
    ctx.drawImage(img, 0, 0)
    
    // 使用最高质量导出PNG
    const pngUrl = canvas.toDataURL('image/png', 1.0)
    // 发送预览URL给父组件
    emit('preview', pngUrl)
    
    // 只有在需要下载时才创建下载链接
    if (needDownload) {
      const link = document.createElement('a')
      link.download = 'mindmap.png'
      link.href = pngUrl
      link.click()
    }
  }
  img.src = svgUrl
}

watch(isRendered, (newValue) => {
  if (newValue) {
    // 当渲染完成时，只生成预览URL，不下载文件
    exportAsPng(false)
  }
})

onMounted(() => {
  if (!svgRef.value) return
  
  try {
    mm = Markmap.create(svgRef.value, {
      duration: 0,
      pan: false,
      zoom: false,
    })
    
    debouncedUpdate()
    window.addEventListener('resize', () => {
      debouncedUpdate()
    })
  } catch (error) {
    console.error('MindMap 初始化错误:', error)
    renderError.value = true
  }
})

watch(() => props.content, debouncedUpdate)

onBeforeUnmount(() => {
  window.removeEventListener('resize', debouncedUpdate)
  debouncedUpdate.cancel()
  mm = null
  isRendered.value = false
})
</script>

<style scoped>
.mind-map-container {
  min-width: unset;
  min-height: 200px;
  max-width: 100%;
  max-height: 85vh;
  background: #fff;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  margin: 0 auto;
  transition: all 0.3s ease;
  border-radius: 8px;
}

/* 响应式样式 */
@media screen and (max-width: 768px) {
  .mind-map-container {
    min-width: unset;
    min-height: 200px;
    padding: 5px;
    margin: 5px auto;
    max-width: 100%;
  }
}

.flex-1 {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
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

:deep(.markmap-node) {
  cursor: pointer;
}

:deep(.markmap-node-circle) {
  fill: #fff;
  stroke-width: 2;
  transition: fill 0.3s ease;
}

:deep(.markmap-node-text) {
  fill: #333;
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-weight: 500;
}

:deep(.markmap-link) {
  stroke: #999;
  stroke-width: 2;
  transition: stroke 0.3s ease;
}

:deep(.markmap-node:hover .markmap-node-circle) {
  fill: #f0f0f0;
}

:deep(.markmap-node:hover .markmap-link) {
  stroke: #666;
}

:deep(svg *[fill="#ffffff"]) {
  fill: transparent !important;
}

:deep(svg *[fill="#fff"]) {
  fill: transparent !important;
}

:deep(svg) {
  max-width: 100% !important;
  max-height: 100% !important;
  pointer-events: none;
}

:deep(.markmap-node) {
  pointer-events: auto;
}

/* 禁用移动端的触摸操作 */
@media (max-width: 768px) {
  :deep(svg) {
    touch-action: none;
    pointer-events: none !important;
  }
  
  :deep(.markmap-node) {
    pointer-events: none !important;
  }
}

/* 桌面端保持可交互 */
@media (min-width: 769px) {
  :deep(svg) {
    pointer-events: none;
  }
  
  :deep(.markmap-node) {
    pointer-events: auto;
  }
}
</style>