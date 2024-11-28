export default {
  home: {
    title: 'Keep Up',
    nav: {
      login: 'Login',
      logout: 'Logout', 
      upload: 'Manual Upload'
    },
    filter: {
      discover: 'Discover Articles by Tag',
      all: 'All',
      channelTitle: 'Select Channels (Multiple)',
      authorTitle: 'Select Authors (Multiple)',
      expand: 'Show More',
      collapse: 'Show Less'
    },
    channels: {
      wechat: 'WeChat',
      youtube: 'YouTube',
      xiaoyuzhou: 'XiaoYuZhou',
      pdf: 'PDF', 
      web: 'Web'
    }
  },
  article: {
    viewOriginal: 'View Original Content',
    sections: {
      title: 'Section Types',
      types: {
        '总结': 'Summary',
        '人物介绍': 'People',
        '名词解释': 'Terms',
        '分段提纲': 'Outline',
        'QA环节': 'Q&A',
        '金句': 'Quotes',
        '分段详述': 'Detailed Outline',
        '引用（测试）': 'References (Beta)',
        '结构图（测试）': 'Structure (Beta)',
        '案例（测试）': 'Cases (Beta)',
        '原文字幕（测试）': 'Original Subtitles (Beta)',
        '翻译字幕（测试）': 'Translated Subtitles (Beta)',
        '彩蛋（测试）': 'Easter Eggs (Beta)'
      }
    },
    fallbackLanguage: {
      zh: 'Chinese',
      en: 'English',
      message: 'Currently displaying {language} content'
    }
  },
  summarize: {
    title: 'Summarize for Me',
    urlPlaceholder: 'Enter article or video content URL',
    languageTitle: 'Select Output Languages',
    languages: {
      zh: 'Chinese',
      en: 'English'
    },
    buttons: {
      cancel: 'Cancel',
      confirm: 'Confirm',
      processing: 'Processing...'
    },
    messages: {
      urlRequired: 'Please enter URL',
      invalidUrl: 'Please enter a valid URL',
      duplicateUrl: 'This URL has already been submitted',
      languageRequired: 'Please select at least one output language',
      submitSuccess: 'Submitted successfully, content is being processed',
      submitFailed: 'Submission failed, please try again',
      maxSelectionsExceeded: 'You can select up to 3 language options'
    },
    summaryLanguageTitle: 'Summary Languages',
    subtitleLanguageTitle: 'Subtitle Languages',
    detailedLanguageTitle: 'Detailed Languages'
  }
} 