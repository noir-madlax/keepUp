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
      message: '当前显示 {language} 内容'
    },
    preview: {
      enlarge: '放大显示'
    }
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
    filePlaceholder: '选择或拖拽文件上传'
  },
  common: {
    retry: '重试',
    loading: '加载中...',
    scrollToLoadMore: '滚动加载更多',
    noMoreData: '没有更多数据了',
    pleaseLogin: '请先登录后再操作'
  },
  upload: {
    card: {
      uploadFile: '点击上传链接',
      supportedPlatforms: '支持播客、油管视频的内容',
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
      }
    }
  }
} 