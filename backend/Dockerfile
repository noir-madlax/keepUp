FROM python:3.11-slim

# 复制证书到容器
COPY ca-bright.crt /usr/local/share/ca-certificates/ca-bright.crt

# 更新证书信任存储
RUN update-ca-certificates

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 