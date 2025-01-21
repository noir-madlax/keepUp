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

### 测试代理配置

可以通过调用 `/router/test` 接口来测试配置的代理是否正常工作:
实际测试的代理地址在.env文件的 `PROXY_LIST` 中

生产环境：
```bash
curl --location --request POST 'https://keep-up-backend.vercel.app/router/test'
```

