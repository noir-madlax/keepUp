export interface ParsedCitation {
  timestamp: string    // [2:01] 或 [1:23:45]
  speaker: string      // Nick Puru
  content: string      // "引用内容"
  isValid: boolean
}

export function parseCitation(markContent: string): ParsedCitation {
  // 匹配格式：*[时间戳] 发言人：\"内容\"* (markdown中的格式)
  // 或：[时间戳] 发言人: "内容" (标准格式)
  // 支持中文冒号和英文冒号
  const markdownCitationRegex = /^\*\[(\d{1,2}(?::\d{2}){1,2})\]\s*([^：:]+?)[:：]\s*[\""](.+?)[\"\"]\*$/s
  const standardCitationRegex = /^\[(\d{1,2}(?::\d{2}){1,2})\]\s*([^：:]+?)[:：]\s*[\""](.+?)[\""]$/s
  
  const content = markContent.trim()
  let match = content.match(markdownCitationRegex) || content.match(standardCitationRegex)
  
  if (match) {
    return {
      timestamp: match[1],
      speaker: match[2].trim(),
      content: match[3].trim(),
      isValid: true
    }
  }
  
  return {
    timestamp: '',
    speaker: '',
    content: markContent,
    isValid: false
  }
}

// 测试用例
export function testCitationParser() {
  const testCases = [
    // 实际数据库中的格式
    `*[2:01] Nick Puru：\"我们要做的是进入Noco，点击我们已经上传的图表，我们将使用这个作为我们的虚拟数据\"*`,
    `*[5:56] Nick Puru：\"我们在技术栈中使用几个不同的工具\"*`,
    
    // 其他可能的格式
    `[2:01] Nick Puru: "我们做的是进入Noco，点击我们已经上传的图表"`,
    `[12:34] John Smith: "This is a test quote with some content"`,
    `[00:00:00]Eric Glyman: "look I think the most important thing"`,
    `[00:15:18]Horace He：这是一个对数刻度`,
    
    // 应该失败的格式
    `No timestamp here: "This should fail"`,
    `[2:01] No quote here`,
  ]
  
  console.log('Citation Parser Test Results:')
  testCases.forEach((testCase, index) => {
    const result = parseCitation(testCase)
    const status = result.isValid ? '✅ PASS' : '❌ FAIL'
    console.log(`Test ${index + 1}: ${status}`)
    console.log(`Input: ${testCase}`)
    if (result.isValid) {
      console.log(`  Timestamp: [${result.timestamp}]`)
      console.log(`  Speaker: ${result.speaker}`)
      console.log(`  Content: "${result.content}"`)
    }
    console.log('---')
  })
} 