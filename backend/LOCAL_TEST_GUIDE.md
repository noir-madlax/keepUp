# 本地测试指南 - YouTube PO Token Script 模式

本指南说明如何在本地开发环境中测试 YouTube PO Token 解决方案（Script 模式）。

## 🎯 **Script 模式的优势**

- ✅ **无需额外服务**：不需要启动 Docker 容器
- ✅ **简单部署**：只需要 Node.js 和 Python 环境
- ✅ **本地友好**：适合本地开发和测试
- ✅ **官方推荐**：bgutil-ytdlp-pot-provider 官方支持

## 📋 **环境要求**

### 1. Node.js 环境
```bash
# 检查 Node.js 版本（需要 >= 18.0）
node --version

# 如果没有安装，请从官网下载
# https://nodejs.org/
```

### 2. Python 环境
```bash
# 检查 Python 版本（推荐 >= 3.8）
python --version

# 确保在虚拟环境中
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

## 🚀 **本地测试步骤**

### 步骤 1：安装依赖

```bash
cd backend

# 安装 Python 依赖（包含 bgutil-ytdlp-pot-provider）
pip install -r requirements.txt

# 验证关键包安装
pip list | grep -E "(yt-dlp|bgutil)"
```

### 步骤 2：运行测试脚本

```bash
# 运行完整测试
python test_youtube_pot.py
```

**预期输出**：
```
YouTube PO Token 配置测试 - Script 模式
============================================================
=== 环境设置建议 ===
✅ 在虚拟环境中运行
✅ Python 版本: 3.11.0
✅ yt-dlp 版本: 2025.6.9

=== 测试 Node.js 环境 ===
✅ Node.js 可用: v18.17.0
✅ npm 可用: 9.6.7

=== 测试 bgutil-ytdlp-pot-provider 插件 ===
✅ bgutil-ytdlp-pot-provider 插件已安装
   版本: 1.1.0

=== 测试 YouTube Fetcher 配置 ===
代理配置: USE_PROXY=True, PROXY_URL=https://your-proxy.com
YouTube 调试: YOUTUBE_DEBUG=False
yt-dlp 配置选项:
  - 客户端: ['mweb']
  - 代理: https://your-proxy.com
  - 安静模式: True
  - User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_6...

=== 测试 YouTube 视频获取 ===
测试 URL: https://www.youtube.com/watch?v=cI1SotLa7Wg
开始获取视频信息...
✅ 成功获取视频信息:
  - 标题: Introducing The VAST AI Operating System
  - 作者: VAST Data
  - 时长: 546 秒
  - 观看次数: 90695

🎉 环境配置正常，可以开始使用 YouTube 视频获取功能
```

### 步骤 3：启动本地服务

```bash
# 启动 FastAPI 服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤 4：测试 API 端点

```bash
# 测试 YouTube 视频获取 API
curl -X POST "http://localhost:8000/api/fetch" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=cI1SotLa7Wg", "language": "zh"}'
```

## 🔧 **调试模式**

如果需要详细的调试信息：

### 1. 启用 YouTube 调试

```bash
# 在 .env 文件中添加
YOUTUBE_DEBUG=true
```

### 2. 查看详细日志

重新运行测试脚本，会看到更多调试信息：
```
YouTube 调试模式已启用
检测到 Node.js: v18.17.0
bgutil-ytdlp-pot-provider 将使用 Script 模式自动生成 PO Token
yt-dlp 配置: 使用 mweb 客户端 + bgutil Script 模式 PO Token 支持
开始提取视频信息，视频ID: cI1SotLa7Wg
使用的 yt-dlp 配置选项: {'quiet': False, 'verbose': True, ...}
```

## ❌ **常见问题排查**

### 1. Node.js 未安装

**错误**：`❌ Node.js 未安装`

**解决**：
```bash
# 下载并安装 Node.js 18+
# https://nodejs.org/

# 验证安装
node --version
npm --version
```

### 2. bgutil 插件未安装

**错误**：`❌ bgutil-ytdlp-pot-provider 插件未安装`

**解决**：
```bash
pip install bgutil-ytdlp-pot-provider==1.1.0
```

### 3. 仍然出现 "Failed to extract any player response"

**可能原因**：
- Node.js 版本过低（< 18.0）
- 网络环境问题
- 代理配置错误

**解决步骤**：
```bash
# 1. 检查 Node.js 版本
node --version

# 2. 启用调试模式
export YOUTUBE_DEBUG=true

# 3. 重新运行测试
python test_youtube_pot.py

# 4. 检查代理设置
curl --proxy YOUR_PROXY_URL https://www.youtube.com
```

## 🚀 **部署到服务器**

本地测试成功后，部署到服务器：

### 使用 Docker（推荐）

```bash
# 构建镜像（已包含 Node.js）
docker build -t keepup-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env keepup-backend
```

### 直接部署

```bash
# 在服务器上安装 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 Python 依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📊 **性能说明**

### Script 模式的工作原理

1. **首次请求**：bgutil 插件调用 Node.js 脚本生成 PO Token
2. **后续请求**：使用缓存的 PO Token（有效期约 6 小时）
3. **自动刷新**：Token 过期时自动重新生成

### 性能特点

- **首次调用**：可能需要 2-5 秒（生成 PO Token）
- **后续调用**：正常速度（使用缓存 Token）
- **内存占用**：比 Docker 模式更低
- **CPU 使用**：仅在生成 Token 时短暂增加

## 🎉 **总结**

Script 模式的优势：
- ✅ **开发友好**：本地测试简单，无需额外服务
- ✅ **部署简单**：只需要 Node.js + Python 环境
- ✅ **资源节省**：不需要额外的 Docker 容器
- ✅ **官方支持**：bgutil-ytdlp-pot-provider 官方推荐方案

这个方案完美解决了本地开发和服务器部署的需求！ 