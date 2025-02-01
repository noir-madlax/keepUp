// 渠道图标映射
const channelIcons: Record<string, string> = {
  'weixin': 'i-mdi-wechat',
  'wechat': 'i-mdi-wechat',
  'zhihu': 'i-mdi-alpha-z-box',
  'juejin': 'i-mdi-alpha-j-box',
  'csdn': 'i-mdi-alpha-c-box',
  'jianshu': 'i-mdi-alpha-j-box',
  'bilibili': 'i-mdi-alpha-b-box',
  'youtube': 'i-mdi-youtube',
  'twitter': 'i-mdi-twitter',
  'medium': 'i-mdi-alpha-m-box',
  'default': 'i-mdi-link'
}

// 获取渠道图标
export const getChannelIcon = (channel?: string): string => {
  if (!channel) return channelIcons.default
  const lowerChannel = channel.toLowerCase()
  return channelIcons[lowerChannel] || channelIcons.default
}

// 获取所有支持的渠道
export const getSupportedChannels = (): string[] => {
  return Object.keys(channelIcons).filter(key => key !== 'default')
}

// 检查是否是支持的渠道
export const isSupportedChannel = (channel: string): boolean => {
  return channel.toLowerCase() in channelIcons
}

// 获取渠道显示名称
export const getChannelDisplayName = (channel: string): string => {
  const channelMap: Record<string, string> = {
    'weixin': '微信',
    'wechat': '微信',
    'zhihu': '知乎',
    'juejin': '掘金',
    'csdn': 'CSDN',
    'jianshu': '简书',
    'bilibili': 'B站',
    'youtube': 'YouTube',
    'twitter': 'Twitter',
    'medium': 'Medium'
  }
  return channelMap[channel.toLowerCase()] || channel
} 