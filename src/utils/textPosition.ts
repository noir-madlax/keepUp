export interface TextMark {
  nodeIndex: number    // 文本节点的索引
  startOffset: number  // 开始位置
  endOffset: number   // 结束位置
  text: string        // 验证用的文本内容
}

export class TextPositionHelper {
  // 本地引用解析方法
  private static parseCitationLocal(markContent: string) {
    const citationRegex = /^\[(\d{1,2}(?::\d{2}){1,2})\]\s*([^:]+?):\s*"(.+?)"$/s
    const match = markContent.trim().match(citationRegex)
    
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

  // 判断是否是需要处理的文本节点
  private static isValidTextNode(node: Node): boolean {
    if (node.nodeType !== Node.TEXT_NODE) return false
    
    const parent = node.parentElement
    if (!parent) return false

    // 排除这些节点:
    // 1. Summary, Question 等 section 头部
    // 2. h1-h6 标题
    // 3. 其他非正文内容
    const excludedTags = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']
    const excludedClasses = ['section-header', 'section-title']
    
    if (excludedTags.includes(parent.tagName)) return false
    
    // 修复: 使用 contains 方法检查类名
    if (excludedClasses.some(cls => parent.classList?.contains(cls))) return false
    
    // 检查是否是 section 类型标记
    if (parent.getAttribute('data-section-type')) return false

    // 确保有非空内容
    return /\S/.test(node.textContent || '')
  }

  // 添加调试信息
  private static logNodeInfo(node: Node, message: string) {
    console.log(message, {
      nodeType: node.nodeType,
      content: node.textContent,
      parent: {
        tag: (node.parentElement?.tagName || 'none'),
        classes: Array.from(node.parentElement?.classList || []),
        attributes: Object.fromEntries(
          Array.from(node.parentElement?.attributes || [])
            .map(attr => [attr.name, attr.value])
        )
      }
    })
  }

  // 获取所有文本节点，并保存正确的索引
  static getTextNodes(element: Element): Array<{node: Text, domIndex: number}> {
    const nodes: Array<{node: Text, domIndex: number}> = []
    
    function collectNodes(node: Node) {
      try {
        if (TextPositionHelper.isValidTextNode(node)) {
          nodes.push({
            node: node as Text,
            domIndex: nodes.length
          })
        } else if (node.childNodes.length > 0) {
          node.childNodes.forEach(child => collectNodes(child))
        }
      } catch (error) {
        // 添加错误处理和调试信息
        console.error('处理节点时出错:', {
          error,
          node: {
            type: node.nodeType,
            content: node.textContent?.slice(0, 100),
            parentTag: node.parentElement?.tagName
          }
        })
      }
    }
    
    collectNodes(element)

    // Debug 信息
    console.log('文本节点列表:', {
      totalNodes: nodes.length,
      nodes: nodes.map((n, i) => ({
        arrayIndex: i,
        domIndex: n.domIndex,
        content: n.node.textContent,
        parentTag: n.node.parentElement?.tagName,
        parentHtml: n.node.parentElement?.innerHTML.slice(0, 50)
      }))
    })

    return nodes
  }

  // 记录位置
  static capturePosition(container: Element, selection: Selection): TextMark | null {
    const range = selection.getRangeAt(0)
    const nodes = this.getTextNodes(container)
    
    // 详细的选择信息
    console.log('选择文本详情:', {
      selectedText: selection.toString(),
      trimmedText: selection.toString().trim(),
      rangeStart: range.startOffset,
      rangeEnd: range.endOffset,
      startContainer: {
        text: range.startContainer.textContent,
        nodeType: range.startContainer.nodeType,
        parentTag: (range.startContainer.parentElement?.tagName || 'none'),
        parentClasses: (range.startContainer.parentElement?.className || 'none')
      }
    })

    // 节点列表详情
    console.log('当前section所有节点:', {
      totalNodes: nodes.length,
      allNodes: nodes.map((n, i) => ({
        index: i,
        domIndex: n.domIndex,
        content: n.node.textContent,
        parentInfo: {
          tag: n.node.parentElement?.tagName,
          classes: n.node.parentElement?.className,
          attributes: Object.fromEntries(
            Array.from(n.node.parentElement?.attributes || [])
              .map(attr => [attr.name, attr.value])
          )
        }
      }))
    })
    
    // 找到对应的节点和它的索引
    const nodeInfo = nodes.find(({node}) => node === range.startContainer)
    if (!nodeInfo) return null

    const mark = {
      nodeIndex: nodeInfo.domIndex,
      startOffset: range.startOffset,
      endOffset: range.endOffset,
      text: selection.toString().trim()
    }

    // 验证位置是否正确
    const actualText = nodeInfo.node.textContent?.slice(mark.startOffset, mark.endOffset)
    if (actualText?.trim() !== mark.text) {
      console.warn('捕获位置可能不正确:', {
        expected: mark.text,
        actual: actualText,
        nodeIndex: mark.nodeIndex,
        node: nodeInfo.node.textContent
      })
    }

    return mark
  }

  // 还原位置
  static findPosition(container: Element, mark: TextMark): Range | null {
    console.log('开始还原标记位置:', {
      mark,
      container: {
        tagName: container.tagName,
        className: container.className,
        attributes: Object.fromEntries(
          Array.from(container.attributes)
            .map(attr => [attr.name, attr.value])
        )
      }
    })

    const nodes = this.getTextNodes(container)
    
    // 打印所有可用节点
    console.log('可用于匹配的节点:', {
      totalNodes: nodes.length,
      targetIndex: mark.nodeIndex,
      allNodes: nodes.map((n, i) => ({
        index: i,
        domIndex: n.domIndex,
        content: n.node.textContent,
        isTarget: n.domIndex === mark.nodeIndex,
        parentInfo: {
          tag: n.node.parentElement?.tagName,
          classes: n.node.parentElement?.className
        }
      }))
    })

    const nodeInfo = nodes.find(({domIndex}) => domIndex === mark.nodeIndex)
    if (!nodeInfo) {
      console.warn('未找到目标节点:', {
        wantedIndex: mark.nodeIndex,
        availableIndexes: nodes.map(n => n.domIndex),
        markInfo: mark
      })
      return null
    }

    const actualText = nodeInfo.node.textContent?.slice(mark.startOffset, mark.endOffset)
    
    // 打印文本匹配结果
    console.log('文本匹配结果:', {
      expected: {
        text: mark.text,
        length: mark.text.length
      },
      actual: {
        text: actualText,
        length: actualText?.length,
        fullNodeText: nodeInfo.node.textContent,
        startOffset: mark.startOffset,
        endOffset: mark.endOffset
      },
      isMatch: actualText?.trim() === mark.text.trim()
    })

    if (actualText?.trim() !== mark.text.trim()) {
      console.warn('文本不匹配详情:', {
        expected: mark.text,
        actual: actualText,
        nodeIndex: mark.nodeIndex,
        fullNodeContent: nodeInfo.node.textContent,
        offsets: {
          start: mark.startOffset,
          end: mark.endOffset
        },
        parent: {
          tag: nodeInfo.node.parentElement?.tagName,
          html: nodeInfo.node.parentElement?.innerHTML
        }
      })
      return null
    }

    try {
      const range = document.createRange()
      range.setStart(nodeInfo.node, mark.startOffset)
      range.setEnd(nodeInfo.node, mark.endOffset)

      // 验证 range 内容
      console.log('Range 内容验证:', {
        rangeText: range.toString(),
        expectedText: mark.text,
        isValid: range.toString().trim() === mark.text.trim()
      })

      return range
    } catch (error) {
      console.error('创建 Range 失败:', error)
      return null
    }
  }

  // 添加新方法：应用标记样式
  static applyMarkStyle(range: Range, markInfo: any): boolean {
    try {
      // 动态导入引用解析器
      const citation = TextPositionHelper.parseCitationLocal(markInfo['mark-content'])
      
      // 创建包装元素
      const wrapper = document.createElement('span')
      
      if (citation.isValid) {
        // 引用格式：使用citation-bubble-wrapper
        wrapper.className = 'citation-bubble-wrapper'
        wrapper.setAttribute('data-citation-info', JSON.stringify(citation))
      } else {
        // 普通标记：使用原有的question-mark-wrapper
        wrapper.className = 'question-mark-wrapper'
        wrapper.classList.add('wavy-underline')
      }
      
      // 设置必要的属性
      wrapper.setAttribute('data-mark-id', markInfo['mark-id'])
      wrapper.setAttribute('data-article-id', markInfo['article-id'])
      wrapper.setAttribute('data-section-type', markInfo['section-type'])
      wrapper.setAttribute('data-mark-content', markInfo['mark-content'])
      wrapper.setAttribute('data-position', markInfo['position'])
      
      // 包装选中的文本
      range.surroundContents(wrapper)

      return true
    } catch (error) {
      console.error('应用标记样式失败:', {
        error,
        markInfo,
        rangeText: range.toString()
      })
      return false
    }
  }
} 