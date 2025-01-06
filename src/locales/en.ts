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
      myUpload: 'My Upload',
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
      webpage: 'Web Page',
      applePodcast: 'Apple Podcast',
      spotify: 'Spotify'
    },
    pullToRefresh: {
      pullDown: 'Pull to refresh',
      release: 'Release to refresh',
      refreshing: 'Refreshing...',
      success: 'Refresh complete'
    },
    network: {
      offline: 'Currently offline',
      weak: 'Weak network connection'
    },
    articles: {
      title: 'Articles'
    }
  },
  article: {
    viewOriginal: 'View Original',
    share: "Share",
    copySuccess: "Link copied",
    sections: {
      title: 'Section Types',
      types: {
        '总结': 'Summary',
        '背景': 'Background',
        '人物介绍': 'Characters',
        '名词解释': 'Terms',
        '分段提纲': 'Section Outline',
        'QA环节': 'Q&A',
        '金句': 'Quotes',
        '分段详述': 'Section Details',
        '引用（测试）': 'References (Test)',
        '结构图': 'Structure',
        '案例（测试）': 'Cases (Test)',
        '原文字幕': 'Original Subtitles',
        '翻译字幕（测试）': 'Translated Subtitles',
        '彩蛋': 'Easter Eggs',
        '思维导图': 'Mind Map',
        '要点总结': 'Key Points',
        '典型案例': 'Typical Cases'
      }
    },
    fallbackLanguage: {
      zh: 'Chinese',
      en: 'English',
      message: 'You are viewing the {language} version,',
      getOtherLanguage: 'click to get summary in other languages'
    },
    preview: {
      enlarge: 'Enlarge View'
    },
    id: 'Article ID',
    originalUrl: 'Original URL',
    getOtherLanguage: 'Get Content in Other Languages',
    fetchSectionsError: 'Failed to fetch article sections status'
  },
  summarize: {
    title: 'Summarize',
    manualupload:'Manual',
    urlPlaceholder: 'Enter Video, Podcast, WebPage URL to summarize',
    languageTitle: 'Select Output Languages',
    languages: {
      zh: 'Chinese',
      en: 'English',
      na: 'Not Now'
    },
    buttons: {
      cancel: 'Cancel',
      confirm: 'Confirm',
      processing: 'Processing...',
      submitting: 'Submitting...'
    },
    messages: {
      urlRequired: 'Please enter URL',
      invalidUrl: 'Please enter a valid URL',
      duplicateUrl: 'This URL has already been submitted',
      languageRequired: 'Please select at least one output language',
      submitSuccess: 'Submitted successfully, content is being processed',
      submitFailed: 'Submission failed, please try again',
      maxSelectionsExceeded: 'You can select up to 3 language options',
      onlyForMedia: 'Only available for video and podcast content'
    },
    summaryLanguageTitle: 'Select the language of the Summary Text:',
    subtitleLanguageTitle: 'Select the language of the Full Transcript:',
    summaryLanguageTitleNote: '(Summarize the most core points)',
    subtitleLanguageTitleNote: '(Extract the full text subtitles)',
    detailedLanguageTitleNote: '(Detail the content of each section)',
    detailedLanguageTitle: 'Select the language of the Section Details:',
    switchToUrl: 'Upload URL',
    switchToFile: 'Upload File',
    dragAndDrop: 'Drag and drop file here',
    or: 'or',
    browseFiles: 'Browse Files',
    supportedFormats: 'Supported formats',
    maxSize: 'Max size',
    removeFile: 'Remove file',
    fileRequired: 'Please select a file',
    fileTooLarge: 'File size cannot exceed 10MB',
    invalidFileType: 'Invalid file type. Please upload DOC, PDF, or TXT files',
    filePlaceholder: 'Select or drag a file to upload',
    moreContent: 'More Content',
    alreadyExists: 'Already Exists',
    supplementSuccess: 'Submitted successfully, content will be available in 5 minutes',
    fileSummaryLanguageTitle: 'Select Summary Language',
    fileSummaryLanguageTitleNote: '(Summarize the core points from the file)',
    uploadProgress: 'Upload Progress: {progress}%',
    uploadComplete: 'Upload Complete',
    uploadFailed: 'Upload Failed',
    fileProcessing: 'File Processing: {progress}%',
    fileProcessingComplete: 'File Processing Complete',
    fileProcessingFailed: 'File Processing Failed',
    summaryLanguageRequired: 'Please select at least one summary language'
  },
  common: {
    retry: 'Retry',
    loading: 'Loading...',
    scrollToLoadMore: 'Scroll to load more',
    noMoreData: 'No more data',
    pleaseLogin: 'Please login first'
  },
  upload: {
    card: {
      uploadFile: 'Click to Upload Link',
      uploadWeb: 'Click to input Web Url',
      supportedPlatforms: 'Support Podcast and Youtube links',
      webLink: 'Any web page URL',
      uploadDoc: 'Click to Upload Files',
      supportedFiles: 'Support Doc/PDF/Txt files up to 10MB',
      fallback: {
        noTitle: 'No Title',
        unknownAuthor: 'Unknown Author',
        unknownDate: 'Unknown Date',
        unknownChannel: 'Unknown Channel',
        unknownTime: 'Unknown Time',
        noLink: 'No Link',
        justNow: 'Just now',
        minutesAgo: '{count} minutes ago',
        hoursAgo: '{count} hours ago',
        daysAgo: '{count} days ago',
        uploaded: 'Uploaded ',
        processing: 'Processing...',
        failed: 'Processing Failed',
        rejected: 'Rejected',
        pending: 'Pending',
        unknownStatus: 'Unknown Status',
        unknownPlatform: 'Unknown Platform'
      },
      error: {
        videoInfo: 'Failed to get video information',
        subtitle: 'Failed to get subtitle content',
        unknown: 'Unknown error'
      },
      action: {
        delete: 'Delete'
      }
    },
    message: {
      deleteSuccess: 'Deleted successfully',
      deleteFailed: 'Failed to delete'
    }
  },
  chat: {
    actions: {
      summary: 'Summary',
      explain: 'Explain',
      question: 'Question'
    },
    input: {
      placeholder: 'How can I help you today?'
    }
  },
  auth: {
    loginSuccess: 'Login successful',
    logoutSuccess: 'Logout successful',
    logoutError: 'Logout failed',
    loginRequired: 'Please login first'
  },
  error: {
    updateFailed: 'Update failed, please try again',
    systemError: 'System error, please try again later',
    articleFetchFailed: 'Failed to fetch article',
    updateSuccess: 'Update successful'
  }
} 