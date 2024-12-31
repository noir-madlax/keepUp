export const isSupportedMediaUrl = (url: string): boolean => {
  const lowercaseUrl = url.toLowerCase()
  return lowercaseUrl.includes('youtube.com') ||
         lowercaseUrl.includes('youtu.be') ||
         lowercaseUrl.includes('spotify.com') ||
         lowercaseUrl.includes('apple.com/podcast')
} 