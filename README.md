# Keep Up (跟牢)

Keep Up 是一个文章收藏和分享平台，帮助用户整理和分享有价值的文章内容。

## 功能特点

- 文章收藏：支持添加各种来源的文章（微信、YouTube、小宇宙、PDF等）
- 标签管理：支持多标签分类（24小时、博客、论文、微信、视频）
- Markdown 支持：文章内容支持 Markdown 格式
- 响应式设计：完美支持移动端和桌面端显示
- 原文链接：保留原文链接方便追溯来源

## 技术栈

- 前端框架：Vue 3 + TypeScript
- 状态管理：Pinia
- UI 框架：Tailwind CSS + Element Plus
- 数据库：Supabase
- 构建工具：Vite
- Markdown 解析：Marked


## 代理测试

### 代理获取和测试

系统包含三个主要的代理相关功能：

#### 1.Proxy Get 接口执行逻辑

1. **初始化**: 创建 ProxyGetter 实例，配置 Webshare API 认证信息

2. **获取代理**:
   - 调用 Webshare API 获取代理列表，每页 100 条
   - 格式化代理信息为标准格式 (http://username:password@address:port)
   - 检查是否有下一页，循环获取所有代理

3. **异步处理**:
   - 每获取一批代理，立即触发后台测试
   - 测试任务通过 POST 请求发送到 `/router/test` 接口
   - 测试接口使用 BackgroundTasks 异步处理，避免 Vercel 5分钟超时限制

4. **结果处理**:
   - 测试通过的代理保存到数据库
   - 返回获取和触发测试的代理总数

```bash
# 本地开发：
curl --location --request POST 'http://localhost:8000/router/get'
# 生产环境：
curl --location --request POST 'https://keep-up-backend.vercel.app/router/get'
```

#### 2. 代理测试1 (proxy_tester1)
测试新数据库表(keep_proxies_list)中的代理：
- 与原tester逻辑相同
- 使用新的数据库表存储结果
- 自动更新代理状态和统计数据
- 支持并发测试多个代理

生产环境：
```bash
curl --location --request POST 'https://keep-up-backend.vercel.app/router/proxy_tester_db'
```

#### 3. 测试代理配置 (原tester)

可以通过调用 `/router/test` 接口来测试配置的代理是否正常工作:
实际测试的代理地址在.env文件的 `PROXY_LIST` 中

```bash
# 生产环境：
curl --location --request POST 'https://keep-up-backend.vercel.app/router/test'
```

