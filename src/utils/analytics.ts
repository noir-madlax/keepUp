import posthog from 'posthog-js'

// 初始化 PostHog
export function initAnalytics() {
  posthog.init('phc_DGaAJ9hMymMkTGniDLXWOPG7oL28zTjxmYaZPpbomDG', { 
    api_host: 'https://app.posthog.com',
    autocapture: true,
    persistence: 'localStorage',
    capture_pageview: true,
    capture_pageleave: true,
  })
}

// 用户身份识别
export function identifyUser(userId: string, userProperties?: Record<string, any>) {
  posthog.identify(userId, {
    ...userProperties,
    $set_once: { // 只在首次设置的属性
      first_seen: new Date().toISOString()
    }
  })
}

// 事件类型定义
export type EventType = 
  | 'article_view'
  | 'article_upload'
  | 'article_upload_success'
  | 'article_upload_failed'
  | 'article_delete'
  | 'article_share'
  | 'article_like'
  | 'article_unlike'
  | 'article_comment'
  | 'article_search'
  | 'article_filter'
  | 'article_sort'
  | 'article_tag_click'
  | 'article_channel_click'
  | 'article_author_click'
  | 'article_click_from_home'
  | 'category_change'
  | 'user_login'
  | 'user_logout'
  | 'user_register'
  | 'user_profile_update'
  | 'user_settings_update'
  | 'page_view'
  | 'error'
  | 'performance'
  | 'session'

// 事件属性类型定义
export interface EventProperties {
  article_id?: string
  article_title?: string
  article_channel?: string
  article_tags?: string[]
  article_author?: string
  article_url?: string
  error_message?: string
  filter_type?: string
  filter_value?: string
  sort_type?: string
  sort_order?: string
  tag_name?: string
  channel_name?: string
  author_name?: string
  user_id?: string
  user_name?: string
  platform?: string
  source?: string
  url?: string
  request_id?: string
  page_name?: string
  page_url?: string
  page_path?: string
  action_time?: string
  error_name?: string
  error_stack?: string
  metric_name?: string
  metric_value?: number
  session_id?: string
  session_start?: string
  [key: string]: any
}

// 事件跟踪函数
export const trackEvent = (
  eventType: EventType,
  properties: EventProperties = {}
) => {
  try {
    // 添加通用属性
    const commonProps = {
      timestamp: new Date().toISOString(),
      platform: 'web',
      environment: import.meta.env.MODE,
      version: import.meta.env.VITE_APP_VERSION || '1.0.0'
    }

    // 合并属性
    const eventData = {
      event: eventType,
      properties: {
        ...commonProps,
        ...properties
      }
    }

    // 发送到分析服务
    if (import.meta.env.PROD) {
      // 生产环境：发送到实际的分析服务
      console.log('Tracking event:', eventData)
      // TODO: 实现实际的分析服务集成
    } else {
      // 开发环境：只打印到控制台
      console.log('Development mode - Tracking event:', eventData)
    }
  } catch (error) {
    console.error('Failed to track event:', error)
  }
}

// 页面访问跟踪
export const trackPageView = (
  pageName: string,
  properties: EventProperties = {}
) => {
  trackEvent('page_view', {
    page_name: pageName,
    page_url: window.location.href,
    page_path: window.location.pathname,
    ...properties
  })
}

// 用户行为跟踪
export const trackUserAction = (
  actionType: EventType,
  properties: EventProperties = {}
) => {
  trackEvent(actionType, {
    action_time: new Date().toISOString(),
    ...properties
  })
}

// 错误跟踪
export const trackError = (
  error: Error,
  properties: EventProperties = {}
) => {
  trackEvent('error', {
    error_name: error.name,
    error_message: error.message,
    error_stack: error.stack,
    ...properties
  })
}

// 性能跟踪
export const trackPerformance = (
  metricName: string,
  value: number,
  properties: EventProperties = {}
) => {
  trackEvent('performance', {
    metric_name: metricName,
    metric_value: value,
    ...properties
  })
}

// 用户会话跟踪
export const trackSession = (
  sessionId: string,
  properties: EventProperties = {}
) => {
  trackEvent('session', {
    session_id: sessionId,
    session_start: new Date().toISOString(),
    ...properties
  })
}

// 导出所有跟踪函数
export const analytics = {
  trackEvent,
  trackPageView,
  trackUserAction,
  trackError,
  trackPerformance,
  trackSession
}

// 设置用户属性
export function setUserProperties(properties: Record<string, any>) {
  posthog.people.set(properties)
}

// 添加用户属性更新方法
export function updateUserProperties(properties: Record<string, any>) {
  posthog.people.set(properties)
} 