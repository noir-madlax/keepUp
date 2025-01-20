import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
// 2024-03-19: 暂时注释掉 PWA 相关配置
// import { VitePWA } from 'vite-plugin-pwa'
import { HttpsProxyAgent } from 'https-proxy-agent'

export default defineConfig({
  base: '/',
  plugins: [
    vue(),
    // 2024-03-19: 暂时移除 PWA 配置
    // VitePWA({...})
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        //  target: 'https://keep-up-backend.vercel.app',
        //  agent: new HttpsProxyAgent('http://127.0.0.1:7890'),
        target: process.env.NODE_ENV === 'production' 
         ? 'https://keep-up-backend.vercel.app'
          : 'http://localhost:8000',
        
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 构建请求头字符串
            const headers = Object.entries(req.headers)
              .filter(([key]) => !['host', 'accept-encoding'].includes(key))
              .map(([key, value]) => `-H '${key}: ${value}'`)
              .join(' ');
    
            // 构建请求体
            let curlCommand = `curl -X ${req.method} '${options.target}${proxyReq.path}'`;
            
            // 添加请求头
            if (headers) {
              curlCommand += ` ${headers}`;
            }
    
            // 2024-03-19: 修复 req.body 类型错误
            const body = (req as any).body;
            if (['POST', 'PUT'].includes(req.method) && body) {
              curlCommand += ` -d '${JSON.stringify(body)}'`;
            }
    
            console.log('\n=== CURL 命令 ===');
            console.log(curlCommand);
            console.log('================\n');
          });
        }
      }
    }
  },
  build: {
    // 2024-03-19: 合并 rollupOptions 配置，添加更严格的缓存控制
    rollupOptions: {
      output: {
        // 确保每次构建生成唯一的文件名
        entryFileNames: `assets/[name].[hash].js`,
        chunkFileNames: `assets/[name].[hash].js`,
        assetFileNames: `assets/[name].[hash].[ext]`,
        // 分包配置
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'article': ['marked'],
          'ui': ['element-plus']
        }
      }
    },
    sourcemap: true,
    assetsDir: 'assets',
    // 2024-03-19: 添加时间戳到构建输出
    assetsInlineLimit: 4096, // 4kb
    // 确保生成的文件名包含内容哈希
    cssCodeSplit: true,
    write: true,
  },
  optimizeDeps: {
    include: [
      // ... existing deps ...
      '@vercel/analytics'
    ]
  }
})
