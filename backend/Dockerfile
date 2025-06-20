FROM python:3.11-slim

# 安装 Node.js (需要 >= 18.0 用于 pytubefix po_token 生成)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 验证 Node.js 安装
RUN node --version && npm --version

# 复制证书到容器
COPY ca-bright.crt /usr/local/share/ca-certificates/ca-bright.crt

# 更新证书信任存储
RUN update-ca-certificates

# 设置Python使用系统证书
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]