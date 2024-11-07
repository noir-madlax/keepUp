export const getChannelIcon = (channel: string): string => {
  const iconMap: Record<string, string> = {
    '微信': 'wechat.svg',
    'YouTube': 'youtube.svg',
    '小宇宙': 'xiaoyuzhou.svg',
    'PDF': 'pdf.svg',
    '网页': 'web.svg'
  }
  return iconMap[channel] || 'default.svg'
} 