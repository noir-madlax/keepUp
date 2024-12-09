<template>
  <div class="mind-map-container flex">
    <svg ref="svgRef" class="flex-1" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

const props = defineProps<{
  content: string
}>()

const svgRef = ref<SVGElement | null>(null)
let mm: any = null
const transformer = new Transformer()

const update = () => {
  if (!mm) return
  const { root } = transformer.transform(props.content)
  mm.setData(root)
  mm.fit()
}

onMounted(() => {
  if (!svgRef.value) return
  
  mm = Markmap.create(svgRef.value)
  
  update()
  
  window.addEventListener('resize', update)
})

watch(() => props.content, update)

onBeforeUnmount(() => {
  window.removeEventListener('resize', update)
  mm = null
})
</script>

<style scoped>
.mind-map-container {
  width: 100%;
  height: 720px;
  background: #fff;
}

:deep(.markmap-node) {
  cursor: pointer;
}

:deep(.markmap-node-circle) {
  fill: #fff;
  stroke-width: 2;
}

:deep(.markmap-node-text) {
  fill: #333;
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

:deep(.markmap-link) {
  stroke: #999;
  stroke-width: 2;
}

:deep(.markmap-node:hover .markmap-node-circle) {
  fill: #f8f8f8;
}
</style>