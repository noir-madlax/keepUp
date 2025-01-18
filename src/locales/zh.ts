export default {
  home: {
    title: 'Keep Up',
    nav: {
      login: '登录',
      logout: '退出',
      upload: '手动上传'
    },
    filter: {
      discover: 'Discover Articles by Tag',
      myUpload: '我的上传',
      all: '全部',
      channelTitle: '频道选择（多选）',
      authorTitle: '作者选择（多选）',
      expand: '展开更多',
      collapse: '收起'
    },
    channels: {
      wechat: '微信',
      youtube: 'YouTube',
      applePodcast: '苹果播客',
      spotify: 'Spotify',
      xiaoyuzhou: '小宇宙',
      pdf: 'PDF',
      webpage: '网页'
    },
    pullToRefresh: {
      pullDown: '下拉刷新',
      release: '释放刷新',
      refreshing: '刷新中...',
      success: '刷新完成'
    },
    network: {
      offline: '当前处于离线状态',
      weak: '网络信号较弱'
    },
    articles: {
      title: '文章'
    }
  },
  article: {
    viewOriginal: '查看原内容',
    share: "分享",
    copySuccess: "链接已复制",
    sections: {
      title: '小节类型选择',
      types: {
        '总结': '总结',
        '人物介绍': '人物介绍',
        '背景': '背景',
        '名词解释': '名词解释',
        '分段提纲': '分段提纲',
        'QA环节': 'QA环节',
        '金句': '金句',
        '分段详述': '分段详述',
        '引用（测试）': '引用（测试）',
        '结构图': '结构图',
        '案例（测试）': '案例（测试）',
        '原文字幕': '原文字幕',
        '翻译字幕（测试）': '翻译字幕',
        '彩蛋': '彩蛋',
        '思维导图': '思维导图',
        '要点总结': '要点总结',
        '典型案例': '典型案例'
      }
    },
    fallbackLanguage: {
      zh: '中文',
      en: '英文',
      message: '当前查看的是{language}版本，',
      getOtherLanguage: '点击获取其他语言版本'
    },
    preview: {
      enlarge: '放大显示'
    },
    id: '文章ID',
    originalUrl: '原始链接',
    getOtherLanguage: '获取其他语言内容',
    fetchSectionsError: '获取文章内容状态失败'
  },
  summarize: {
    title: '总结',
    manualupload:'手工',
    urlPlaceholder: '输入要总结的视频、播客、网页链接或者文档',
    languageTitle: '选择输出语言',
    languages: {
      zh: '中文',
      en: '英文',
      na: '暂不需要'
    },
    buttons: {
      cancel: '取消',
      confirm: '确定',
      processing: '处理中...',
      submitting: '提交中...'
    },
    messages: {
      urlRequired: '请输入URL',
      invalidUrl: '请输入有效的URL地址',
      duplicateUrl: '该链接已经提交过了',
      duplicateUrlAutoRedirect: '该文章已存在，2秒后将自动跳转到文章页面...',
      click: '点击',
      toViewExistingArticle: '查看已有文章',
      languageRequired: '请选择一种输出语言',
      submitSuccess: '提交成功，内容正在处理中',
      submitFailed: '提交失败，请重试',
      maxSelectionsExceeded: '最多只能选择3个语言选项',
      onlyForMedia: '只支持视频和播客类型的内容'
    },
    summaryLanguageTitle: '选择总结语言',
    summaryLanguageTitleNote: '(根据原文总结出最核心的要点)',
    subtitleLanguageTitle: '选择字幕语言',
    subtitleLanguageTitleNote: '(从原始内容中提取全文字幕)',
    detailedLanguageTitle: '选择分段详述语言',
    detailedLanguageTitleNote: '(详细叙述原文每个分段的内容)',
    switchToUrl: '上传链接',
    switchToFile: '上传文件',
    dragAndDrop: '拖拽文件到这里',
    or: '或',
    browseFiles: '浏览文件',
    supportedFormats: '支持的格式',
    maxSize: '最大大小',
    removeFile: '移除文件',
    fileRequired: '请选择文件',
    fileTooLarge: '文件大小不能超过10MB',
    invalidFileType: '不支持的文件类型，请上传DOC、PDF或TXT文件',
    filePlaceholder: '选择或拖拽文件上传',
    moreContent: '更多内容',
    alreadyExists: '已存在',
    supplementSuccess: '提交成功，内容将在5分钟后可见',
    fileSummaryLanguageTitle: '选择总结语言',
    fileSummaryLanguageTitleNote: '(从文件中总结出核心要点)',
    uploadProgress: '上传进度: {progress}%',
    uploadComplete: '上传完成',
    uploadFailed: '上传失败',
    fileProcessing: '文件处理中: {progress}%',
    fileProcessingComplete: '文件处理完成',
    fileProcessingFailed: '文件处理失败',
    summaryLanguageRequired: '请至少选择一种总结语言'
  },
  common: {
    retry: '重试',
    loading: '加载中...',
    scrollToLoadMore: '滚动加载更多',
    noMoreData: '没有更多数据了',
    pleaseLogin: '请先登录后再操作',
    edit: '编辑文章',
    cancel: '取消',
    save: '保存',
    close: '关闭',
    preview: '预览思维导图',
    processing: '处理中',
    askAI: '询问AI',
    more: '更多',
    loginToViewMore: '请登录后查看更多内容'
  },
  upload: {
    card: {
      uploadFile: '点击上传链接',
      supportedPlatforms: '支持Youtube视频、Apple和Spotify的播客',
      uploadWeb: '点击总结网页',
      webLink: '任何网页的URL链接',
      uploadDoc: '点击总结文档',
      supportedFiles: '支持10mb内的Doc、PDF、Txt文档',
      fallback: {
        noTitle: '无标题',
        unknownAuthor: '未知作者',
        unknownDate: '未知日期',
        unknownChannel: '未知频道',
        unknownTime: '未知时间',
        noLink: '无链接',
        justNow: '刚刚',
        minutesAgo: '{count}分钟前',
        hoursAgo: '{count}小时前',
        daysAgo: '{count}天前',
        uploaded: '上传于 ',
        processing: '处理中...',
        failed: '处理失败',
        rejected: '已拒绝',
        pending: '等待处理',
        unknownStatus: '未知状态'
      },
      error: {
        videoInfo: '无法获取视频信息',
        subtitle: '无法获取字幕内容',
        unknown: '其他原因'
      },
      action: {
        delete: '删除'
      }
    },
    message: {
      deleteSuccess: '删除成功',
      deleteFailed: '删除失败'
    }
  },
  chat: {
    actions: {
      explain: '解释含义',
      elaborate: '展开详述',
      question: '自由提问',
      structure: '内容结构图',
      overview: '分段提纲',
      quotes: '金句',
      xmind: '思维导图',
      expand: '展开说说',
      original: '给出原文',
      explain_selection: '解释一下',
      expand_prompt: '请详细展开解释这段内容的含义和背景，用通俗易懂的方式说明。',
      original_prompt: '请给出这段内容的完整原文，并标注出重要的关键词和短语。',
      explain_selection_prompt: '请解释这段内容中的专业术语和难懂概念，帮助我更好地理解。'
    },
    input: {
      placeholder: '需要我为您做些什么？'
    },
    window: {
      title: 'AI 助手',
      sessionSelect: '选择会话',
      startChat: '开始对话...',
      send: '发送'
    },
    questionMark: '问题',
    toolbar: {
      hint: '🌟选中文字,进一步提问了解更多:'
    },
    errors: {
      userNotLoggedIn: '用户未登录',
      createSessionFailed: '创建会话失败',
      createOrGetSessionFailed: '无法创建或获取会话',
      sessionNotFound: '未找到会话',
      invalidSessionData: '会话数据无效',
      loadSessionFailed: '加载会话失败，请重试',
      noCurrentArticle: '没有当前文章ID',
      initSessionFailed: '初始化会话失败',
      sendMessageFailed: '发送消息失败，请重试',
      loadSessionListFailed: '加载会话列表失败',
      reloadMessageFailed: '重新加载消息失败，请刷新页面重试',
      aiResponseFailed: 'AI 响应加载失败，正在重试...'
    }
  },
  auth: {
    loginSuccess: '登录成功',
    logoutSuccess: '已退出登录',
    logoutError: '退出失败',
    loginRequired: '请先登录',
    logoutSuccessMessage: '已退出登录',
    logoutFailedMessage: '退出失败，请重试'
  },
  error: {
    updateFailed: '更新失败，请重试',
    systemError: '系统错误，请稍后重试',
    articleFetchFailed: '获取文章失败',
    updateSuccess: '更新成功',
    requiredFields: '标题、内容和作者为必填项',
    getAuthorsFailed: '获取作者列表失败',
    loginFirst: '请登录',
    submitArticleFailed: '系统错误，请稍后重试',
    requiredArticleFields: '标题、内容和作者为必填项',
    getArticleDetailsFailed: '获取文章详情失败',
    dateFormatError: '日期格式化错误',
    fetchArticleListFailed: '获取文章列表失败，请稍后重试'
  }
} 