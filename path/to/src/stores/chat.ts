const handleSSE = async (
  url: string, 
  init: RequestInit,
  onMessage: (data: any) => void,
  onDone: () => void,
  onError: (error: any) => void
) => {
  try {
    const response = await fetch(url, init)
    if (!response.ok) {
      throw new Error(`网络响应不是 OK: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader!.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      let boundary = buffer.indexOf('\n\n')
      while (boundary !== -1) {
        const chunk = buffer.slice(0, boundary)
        buffer = buffer.slice(boundary + 2)
        if (chunk.startsWith('data: ')) {
          const dataStr = chunk.slice(6)
          if (dataStr === '[DONE]') {
            onDone()
            return
          }
          try {
            const data = JSON.parse(dataStr)
            onMessage(data)
          } catch (err) {
            console.error('解析 SSE 数据失败:', err)
          }
        }
        boundary = buffer.indexOf('\n\n')
      }
    }
  } catch (error) {
    onError(error)
  }
} 