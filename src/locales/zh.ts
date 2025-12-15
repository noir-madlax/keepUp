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
      myUpload: 'Recent Uploads',
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
      title: 'Summaries'
    },
    earlyAccess: {
      title: '🎉Early Access - Experience Keep Up Now!',
      card: {
        title: 'Early Access Privileges',
        privileges: {
          aiSummary: 'Unlimited Summaries',
          priorityAccess: 'Free AI Chat',
          feedback: 'VIP Feedback Channel',
          discount: 'Premium Discounts'
        }
      },
      feedback: 'Dear early adopters, your feedback matters and shapes our future📨'
    }
  },
  article: {
    viewOriginal: 'View Original',
    share: "Share",
    delete: "删除",
    deleteConfirm: "确定要删除这篇文章吗？删除后将不会在首页显示，但仍可通过链接访问。",
    deleteSuccess: "文章已删除",
    deleteFailed: "删除失败，请重试",
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
        '典型案例': 'Typical Cases',
        '额外补充': 'Additional Processing'
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
    title_early: '🎉Early Access🎉  AI Summary',
    manualupload:'Manual',
    urlPlaceholder: 'Place any Youtube or Podcast link here to summarize',
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
      duplicateUrlAutoRedirect: 'This article already exists, redirecting to the article page in 2 seconds...',
      click: 'click',
      toViewExistingArticle: 'to view existing article',
      languageRequired: 'Please select at least one output language',
      submitSuccess: 'Submitted successfully, content will be available IN 2 MINUTES ',
      submitFailed: 'Submission failed, please try again',
      maxSelectionsExceeded: 'You can select up to 3 language options',
      onlyForMedia: 'Only available for video and podcast content',
      submitting: 'Processing your request, please wait...'
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
    supplementSuccess: 'Submitted successfully, content will be available in 2 minutes',
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
    pleaseLogin: 'Please login first',
    edit: 'Edit Article',
    cancel: '取消',
    confirm: '确定',
    warning: '警告',
    save: 'Save',
    close: 'Close',
    preview: 'Preview Mind Map',
    processing: 'Processing',
    askAI: 'Ask AI',
    more: 'More',
    loginToViewMore: 'Paste a link to see summaries in 2 minutes'
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
        unknown: 'Failed to process your link'
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
      explain: 'Explain Meaning',
      elaborate: 'Elaborate Details',
      question: 'Ask Question',
      structure: 'Content Structure',
      overview: 'Section Outline',
      quotes: 'Key Quotes',
      xmind: 'Mind Map',
      expand: '展开说说',
      original: '分享',
      explain_selection: 'Explain This',
      expand_prompt: 'Please explain this content in detail, including more specific details based on the original context.',
      original_prompt: 'Please check my input content above.And provide the complete original text and highlight important keywords.',
      explain_selection_prompt: 'Please explain the specific meaning of this content based on the original context.'
    },
    input: {
      placeholder: 'How can I help you today?'
    },
    window: {
      title: 'AI Assistant',
      sessionSelect: 'Select Session',
      startChat: 'Ask me anything about the article',
      send: 'Send'
    },
    questionMark: 'Question',
    toolbar: {
      hint: '🎉Ask follow up questions about the content:',
      selected_hint: '🎉Ask follow up questions about the selected text:',
      hover_hint: 'Select text to ask AI questions'
    },
    errors: {
      userNotLoggedIn: 'Please login first',
      createSessionFailed: 'Failed to create session',
      createOrGetSessionFailed: 'Failed to create or get session',
      sessionNotFound: 'Session not found',
      invalidSessionData: 'Invalid session data',
      loadSessionFailed: 'Failed to load session, please try again',
      noCurrentArticle: 'No current article ID',
      initSessionFailed: 'Failed to initialize session',
      sendMessageFailed: 'Failed to send message, please try again',
      loadSessionListFailed: 'Failed to load session list',
      reloadMessageFailed: 'Failed to reload message, please refresh the page',
      aiResponseFailed: 'AI response loading failed, retrying...'
    }
  },
  auth: {
    login: {
      title: 'Login',
      subtitle: 'Choose a login method to continue',
      githubButton: 'Login with GitHub',
      googleButton: 'Login with Google',
      error: 'Login failed, please try again'
    },
    loginSuccess: 'Login successful',
    logoutSuccess: 'Logout successful',
    logoutError: 'Logout failed',
    loginRequired: 'Please login first',
    logoutSuccessMessage: 'Logged out successfully',
    logoutFailedMessage: 'Logout failed, please try again'
  },
  error: {
    updateFailed: 'Update failed, please try again',
    systemError: 'System error, please try again later',
    articleFetchFailed: 'Failed to fetch article',
    updateSuccess: 'Update successful',
    requiredFields: 'Title, content and author are required',
    getAuthorsFailed: 'Failed to get authors list',
    loginFirst: 'Please login',
    submitArticleFailed: 'System error, please try again later',
    requiredArticleFields: 'Title, content and author are required',
    getArticleDetailsFailed: 'Failed to get article details',
    dateFormatError: 'Date format error',
    fetchArticleListFailed: 'Failed to get article list, please try again later'
  }
} 