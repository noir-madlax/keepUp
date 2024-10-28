/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'vue-markdown-render' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{
    source: string
  }>
  export default component
}

declare module 'vue-router'
declare module 'pinia'
