export interface ParsedCitation {
  timestamp: string    // e.g. 2:01 or 01:23:45; empty string when no valid timestamp
  speaker: string      // speaker name
  content: string      // quote content
  isValid: boolean
}

// Determine whether a label inside brackets is a meaningful timestamp.
// Supports m:ss, mm:ss, h:mm:ss, hh:mm:ss. All-zero values (00:00, 0:00, 00:00:00) are treated as invalid.
export function isMeaningfulTimestamp(label: string | undefined | null): boolean {
  if (!label) return false
  const raw = String(label).trim()
  const timeRegex = /^(\d{1,2}:\d{2})(?::\d{2})?$/
  if (!timeRegex.test(raw)) return false
  if (raw === '00:00' || raw === '0:00' || raw === '00:00:00') return false
  const parts = raw.split(':').map(n => parseInt(n, 10))
  if (parts.length === 2) {
    const [, s] = parts
    return s >= 0 && s < 60
  }
  if (parts.length === 3) {
    const [, m, s] = parts
    return m >= 0 && m < 60 && s >= 0 && s < 60
  }
  return false
}

export function parseCitation(markContent: string): ParsedCitation {
  // Supported formats:
  // 1) *[timestamp or label] Speaker："content"*
  // 2) [timestamp or label] Speaker: "content"
  // 3) Speaker："content"  (no brackets)
  // Works with Chinese/English colon and quotes
  const citationRegex = /^(?:\*?\[(.+?)\]\s*)?([^：:]+?)[:：]\s*["“”](.+?)["“”]\*?$/s

  const content = markContent.trim()
  const match = content.match(citationRegex)

  if (match) {
    const possibleLabel = match[1]?.trim() || ''
    const ts = isMeaningfulTimestamp(possibleLabel) ? possibleLabel : ''
    return {
      timestamp: ts,
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

// Simple test helper
export function testCitationParser() {
  const testCases = [
    // Existing DB-like formats
    `*[2:01] Nick Puru："我们要做的是进入Noco，点击我们已经上传的图表，我们将使用这个作为我们的虚拟数据"*`,
    `*[5:56] Nick Puru："我们在技术栈中使用几个不同的工具"*`,

    // Other formats
    `[2:01] Nick Puru: "我们做的是进入Noco，点击我们已经上传的图表"`,
    `[12:34] John Smith: "This is a test quote with some content"`,
    `[00:00:00]Eric Glyman: "look I think the most important thing"`, // all-zero will be treated as invalid timestamp
    `[00:15:18]Horace He：这是一个对数刻度`,
    `*[分析时] 肖风："我们希望香港的经验能够为…"*`, // non-time label → timestamp hidden
    `Harrison Chase："智能体是…"`, // no brackets → timestamp hidden

    // Should fail
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