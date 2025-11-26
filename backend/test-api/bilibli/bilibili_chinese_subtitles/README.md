# B站中文字幕获取工具

## 概述
这是一个专门获取B站视频中文字幕的Python脚本，改进自原版测试脚本。

## 主要改进

### 1. 只获取中文字幕
- ✅ **过滤语言**: 只下载中文字幕（ai-zh、zh-CN、zh-Hant等）
- ⏭️ **跳过其他语言**: 自动跳过英文、日文等其他语言字幕
- 📊 **详细统计**: 显示中文字幕行数和预览

### 2. 功能增强
- 🔍 **智能识别**: 通过语言代码和描述双重判断中文字幕
- 📁 **独立目录**: 结果保存在project1/output目录
- 📈 **完整获取**: 确保获取视频完整字幕内容

## 文件结构
```
project1/
├── test_bilibili_chinese_subtitles.py  # 主脚本
├── output/                            # 输出目录
│   ├── chinese_subtitle_srt_*.srt     # SRT格式中文字幕
│   ├── chinese_subtitle_raw_*.json    # 原始JSON格式字幕
│   ├── video_info_*.json              # 视频基本信息
│   └── player_info_*.json             # 播放器信息
└── README.md                          # 说明文件
```

## 使用方法

### 1. 准备Cookie文件
需要在父目录的 `ok-result/blibli-cookie.txt` 中放置B站登录cookie。

### 2. 运行脚本
```bash
cd backend/test-api/project1
python3 test_bilibili_chinese_subtitles.py
```

### 3. 修改目标视频
在脚本的 `main()` 函数中修改 `video_url` 变量：
```python
video_url = "https://www.bilibili.com/video/BV1sWobYuEa6"  # 修改为目标视频
```

## 测试结果对比

### 新脚本 (BV1sWobYuEa6)
- ✅ **中文字幕**: 354行完整字幕
- 📊 **视频时长**: 640秒 (约10分40秒)
- 📄 **覆盖范围**: 00:00:00 - 00:10:38

### 原脚本 (BV1Bz421h7B1)  
- ⚠️ **字幕较少**: 89行字幕
- 📊 **覆盖范围**: 00:00:10 - 00:12:46
- 🤔 **可能原因**: 视频本身字幕较少或获取不完整

## 中文字幕识别规则

脚本通过以下规则识别中文字幕：

### 语言代码匹配
- `ai-zh`: AI生成中文字幕
- `zh-CN`: 简体中文
- `zh-Hant`: 繁体中文
- `zh`: 中文
- `zh-Hans`: 简体中文

### 描述关键词匹配
- 中文、简体、繁体、中字、汉语

## 注意事项
1. 需要有效的B站登录Cookie
2. 某些视频可能没有中文字幕
3. 脚本会自动跳过非中文字幕，只处理中文内容
4. 输出文件包含时间戳，避免覆盖之前的结果 