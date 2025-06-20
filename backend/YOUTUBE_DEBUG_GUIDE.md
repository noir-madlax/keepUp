# YouTube 获取问题调试指南

## 问题现象
服务器环境中出现 `Failed to extract any player response` 错误，本地环境正常。

## 快速诊断

### 1. 运行环境诊断脚本
```bash
cd backend
python3 diagnose_server_env.py
```

### 2. 查看详细日志
在服务器上测试 YouTube 获取时，查看日志中的关键信息：

**成功的标志**：
- `[pot] PO Token Providers: bgutil:http-1.1.0 (external), bgutil:script-1.1.0 (external)`
- `✅ Node.js 版本: v18.x.x` (或更高)
- `✅ bgutil-ytdlp-pot-provider 包已安装`

**失败的标志**：
- `Failed to extract any player response`
- `❌ Node.js 不可用`
- `❌ bgutil-ytdlp-pot-provider 包未安装`

## 常见问题和解决方案

### 问题 1: Node.js 未安装或版本过低
**现象**：
```
❌ Node.js 不可用
❌ Node.js 版本过低，需要 >= 18.0
```

**解决方案**：
```bash
# 检查 Dockerfile 中的 Node.js 安装
# 确保包含以下内容：
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
```

### 问题 2: bgutil 插件未正确安装
**现象**：
```
❌ bgutil-ytdlp-pot-provider 包未安装
❌ 无法导入 bgutil_ytdlp_pot_provider
```

**解决方案**：
```bash
# 重新安装 bgutil 插件
pip3 install --force-reinstall bgutil-ytdlp-pot-provider==1.1.0

# 验证安装
pip3 show bgutil-ytdlp-pot-provider
```

### 问题 3: yt-dlp 插件目录问题
**现象**：
```
❌ 未找到 yt_dlp_plugins 目录
⚠️ 未找到 bgutil 相关插件
```

**解决方案**：
```bash
# 检查 Python site-packages 路径
python3 -c "import site; print(site.getsitepackages())"

# 手动创建插件目录（如果需要）
mkdir -p /usr/local/lib/python3.11/site-packages/yt_dlp_plugins

# 重新安装 yt-dlp
pip3 install --force-reinstall yt-dlp==2025.6.9
```

### 问题 4: 容器环境权限问题
**现象**：
- 包已安装但无法正常工作
- 权限相关错误

**解决方案**：
```bash
# 在 Dockerfile 中添加权限设置
RUN chmod +x /usr/local/bin/node
RUN chmod -R 755 /usr/local/lib/python*/site-packages/
```

### 问题 5: 网络环境问题
**现象**：
```
Error reaching GET http://127.0.0.1:4416/ping
Failed to extract any player response
```

**解决方案**：
1. 检查代理设置
2. 尝试不同的客户端配置
3. 使用备用方案

## 验证修复

### 1. 运行完整测试
```bash
python3 test_youtube_pot.py
```

### 2. 检查关键日志
成功的日志应该包含：
```
✅ Node.js 版本: v18.20.8
✅ bgutil-ytdlp-pot-provider 包已安装
[pot] PO Token Providers: bgutil:http-1.1.0 (external), bgutil:script-1.1.0 (external)
✅ 成功获取视频信息
```

### 3. 测试实际 API 调用
使用测试 URL 验证：
```bash
curl -X POST http://localhost:8000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=cI1SotLa7Wg"}'
```

## Docker 环境特殊配置

### 完整的 Dockerfile 示例
```dockerfile
FROM python:3.11-slim

# 安装 Node.js 18.x
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    node --version && npm --version

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 验证关键包安装
RUN pip3 show bgutil-ytdlp-pot-provider && \
    pip3 show yt-dlp

# 设置工作目录
WORKDIR /app
COPY . .

# 运行诊断（可选，用于调试）
RUN python3 diagnose_server_env.py || true

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 故障排除步骤

1. **基础环境检查**
   ```bash
   python3 --version
   node --version
   pip3 list | grep -E "(yt-dlp|bgutil)"
   ```

2. **运行诊断脚本**
   ```bash
   python3 diagnose_server_env.py
   ```

3. **检查详细日志**
   - 启用 `YOUTUBE_DEBUG=True`
   - 查看 yt-dlp 调试输出

4. **逐步测试**
   - 先测试基本的 yt-dlp 功能
   - 再测试 bgutil 插件集成
   - 最后测试完整的 API 调用

5. **网络问题排查**
   - 检查代理设置
   - 测试不同的 YouTube URL
   - 尝试不同的客户端配置

## 联系支持

如果问题仍然存在，请提供：
1. `diagnose_server_env.py` 的完整输出
2. 详细的错误日志（启用 YOUTUBE_DEBUG=True）
3. 服务器环境信息（操作系统、Docker 版本等）
4. 网络环境信息（是否使用代理、防火墙设置等） 