# B站视频总结集成设计文档

## 1. 项目概述

### 1.1 目标
在keepup系统中增加对bilibili视频的支持，用户可以贴入B站视频链接，系统自动获取字幕内容并生成总结文章。

### 1.2 设计原则
- **最小化变更**：只添加必要组件，不影响现有逻辑
- **复用现有架构**：遵循现有的Parser+Fetcher模式
- **简化数据获取**：只获取系统必需的字段，避免复杂爬虫功能

## 2. 现有系统分析

### 2.1 核心流程
1. 前端 `ArticleRequestForm.vue` 提交链接
2. `ContentResolver` 使用 `PlatformParser` 解析URL → 返回(platform, parsed_url, original_url)
3. `ContentFetcherService` 使用 `ContentFetcher` 获取内容 → 返回VideoInfo
4. 调用Coze API处理内容，生成文章存储到数据库
5. 前端展示文章

### 2.2 必要数据结构
- **VideoInfo**: `{title, description, author, article}`
- **AuthorInfo**: 作者基本信息
- **ArticleCreate**: 文章创建数据

### 2.3 Cookie管理
- 已存储在 `keep_prompt` 表，类型为 `cookie-bilbli`
- 包含完整的认证信息(SESSDATA, bili_jct, DedeUserID等)

## 3. 必要变更清单

### 3.1 新增组件

#### A. BilibiliParser - 平台解析器
- **文件**: `backend/app/services/platform_parser/bilibili.py`
- **功能**: 
  - 识别B站URL格式(BV号、av号、短链接、手机端)
  - 标准化URL格式
  - 返回("bilibili", standardized_url, original_url)
- **最小实现**: 只支持基础URL识别和转换

#### B. BibiliFetcher - 内容获取器
- **文件**: `backend/app/services/content_fetcher/bilibili.py`
- **功能**:
  - 从数据库获取cookie配置
  - 调用B站API获取视频基本信息
  - 获取中文字幕内容
  - 构造VideoInfo对象
- **简化策略**: 
  - 只获取第一个分页的字幕
  - 只获取中文字幕(ai-zh)
  - 基本的错误处理

### 3.2 集成点修改

#### A. ContentResolver集成
- **文件**: `backend/app/services/content_resolver.py`
- **变更**: 在parsers列表中添加BilibiliParser()
- **位置**: 第13行parsers列表

#### B. ContentFetcherService集成
- **文件**: `backend/app/services/content_fetcher/service.py`
- **变更**: 
  - 导入BilibilitFetcher
  - 在fetchers列表中添加BilibilitFetcher()
- **位置**: 第17行fetchers列表

### 3.3 前端最小化支持

#### A. 平台识别
- **文件**: `src/utils/channel.ts`
- **变更**: 添加bilibili平台检测逻辑
- **图标**: 复用现有的video.svg或添加bilibili.svg

#### B. 平台显示
- **文件**: `src/components/ArticleCard.vue`
- **变更**: 添加bilibili平台的显示样式(如果需要特殊处理)

## 4. 核心实现逻辑

### 4.1 URL解析逻辑
```
支持格式:
- https://www.bilibili.com/video/BV1xxx
- https://bilibili.com/video/av12345
- https://b23.tv/xxx (短链接)
- https://m.bilibili.com/video/xxx (手机端)

统一转换为: https://www.bilibili.com/video/{BV号}
```

### 4.2 Cookie获取逻辑
```
从 keep_prompt 表获取 type='cookie-bilbli' 的记录
解析JSON格式的cookie数据
提取关键字段: SESSDATA, bili_jct, DedeUserID, buvid3
构造请求头
```

### 4.3 内容获取流程
```
1. 提取BV号 → extract_bv_id()
2. 获取视频信息 → /x/web-interface/view API
3. 获取播放器信息 → /x/player/v2 API  
4. 筛选中文字幕 → 只处理ai-zh类型
5. 下载字幕内容 → 获取subtitle_url内容
6. 构造VideoInfo对象返回
```

### 4.4 必要字段映射
```
VideoInfo构造:
- title: 视频标题
- description: 字幕文本内容(拼接所有字幕行)
- author: {"name": UP主名称, "icon": 头像URL, "channel_id": mid}
- article: ArticleCreate对象(channel="bilibili")
```

## 5. 错误处理策略

### 5.1 最小化错误处理
- Cookie失效: 返回None，记录日志
- 视频无字幕: 返回基本视频信息，description为空
- API请求失败: 重试1次，失败则返回None
- 权限问题: 记录日志，返回None

### 5.2 降级方案
- 如果无法获取字幕，使用视频标题和简介作为内容
- 如果无法获取作者信息，使用默认值

## 6. 配置需求

### 6.1 环境变量
无需新增环境变量，使用现有数据库配置

### 6.2 数据库依赖
依赖现有的 `keep_prompt` 表中的cookie配置

## 7. 测试策略

### 7.1 集成测试
- 使用现有的test代码中的示例视频
- 测试URL解析的各种格式
- 测试字幕获取和内容处理

### 7.2 错误场景测试
- Cookie失效场景
- 私有视频场景
- 无字幕视频场景

## 8. 部署注意事项

### 8.1 依赖管理
无需新增Python依赖，使用现有的requests库

### 8.2 性能考虑
- 字幕内容较长时的内存使用
- API请求频率限制

## 9. 后续扩展预留

### 9.1 功能扩展点
- 支持多分页视频
- 支持多语言字幕选择
- 支持视频章节信息
- 更详细的作者信息获取

### 9.2 优化空间
- Cookie自动刷新机制
- 内容缓存策略
- 字幕质量评估

## 10. 风险评估

### 10.1 技术风险
- B站API变更风险: 中等
- Cookie失效风险: 高
- 反爬虫风险: 中等

### 10.2 缓解措施
- 监控API响应状态
- 准备Cookie更新机制
- 实现优雅降级

---

**总结**: 此设计采用最小化变更原则，只新增2个核心文件和4个集成点修改，充分复用现有架构，可快速实现B站视频总结功能。 