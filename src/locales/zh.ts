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
      web: '网页'
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
        '名词解释': '名词解释',
        '分段提纲': '分段提纲',
        'QA环节': 'QA环节',
        '金句': '金句',
        '分段详述': '分段详述',
        '引用（测试）': '引用（测试）',
        '结构图': '结构图',
        '案例（测试）': '案例（测试）',
        '原文字幕': '原文字幕',
        '翻译字幕（测试）': '翻译字幕（测试）',
        '彩蛋（测试）': '彩蛋（测试）',
        '思维导图': '思维导图',
        '要点总结': '要点总结'
      }
    },
    fallbackLanguage: {
      zh: '中文',
      en: '英文',
      message: '当前显示 {language} 内容'
    }
  },
  summarize: {
    title: '上传',
    manualupload:'手工',
    urlPlaceholder: '输入视频、播客内容的链接',
    languageTitle: '选择输出语言',
    languages: {
      zh: '中文',
      en: '英文'
    },
    buttons: {
      cancel: '取消',
      confirm: '确定',
      processing: '处理中...'
    },
    messages: {
      urlRequired: '请输入URL',
      invalidUrl: '请输入有效的URL地址',
      duplicateUrl: '该链接已经提交过了',
      languageRequired: '请至少选择一种输出语言',
      submitSuccess: '提交成功，内容正在处理中',
      submitFailed: '提交失败，请重试',
      maxSelectionsExceeded: '最多只能选择3个语言选项'
    },
    summaryLanguageTitle: '总结语言',
    subtitleLanguageTitle: '全文字幕',
    detailedLanguageTitle: '分段详述'
  },
  common: {
    retry: '重试',
    loading: '加载中...',
    scrollToLoadMore: '滚动加载更多',
    noMoreData: '没有更多数据了'
  }
} 