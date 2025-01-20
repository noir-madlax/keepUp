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

// 追踪自定义事件
export function trackEvent(eventName: string, properties?: Record<string, any>) {
  posthog.capture(eventName, properties)
}

// 设置用户属性
export function setUserProperties(properties: Record<string, any>) {
  posthog.people.set(properties)
}

// 添加用户属性更新方法
export function updateUserProperties(properties: Record<string, any>) {
  posthog.people.set(properties)
}

// 添加用户行为追踪方法
export function trackUserAction(eventName: string, properties?: Record<string, any>) {
  posthog.capture(eventName, {
    ...properties,
    timestamp: new Date().toISOString()
  })
} 