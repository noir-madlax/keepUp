import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { VitePWA } from 'vite-plugin-pwa'
import { HttpsProxyAgent } from 'https-proxy-agent'

export default defineConfig({
  base: '/',
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Keep Up',
        short_name: 'Keep Up',
        description: '文章收藏和分享平台',
        theme_color: '#ffffff',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        clientsClaim: true,
        skipWaiting: true,
        cleanupOutdatedCaches: true,
        runtimeCaching: [
          {
            urlPattern: /\/$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'html-cache',
              expiration: {
                maxAgeSeconds: 60 * 60 * 24
              }
            }
          },
          {
            urlPattern: /^https:\/\/.*\.supabase\.co\/.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxAgeSeconds: 60 * 60
              },
              matchOptions: {
                ignoreSearch: false,
                ignoreVary: false
              }
            }
          },
          {
            urlPattern: /\.(js|css|png|jpg|jpeg|svg|gif)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'static-resources',
              expiration: {
                maxAgeSeconds: 60 * 60 * 24 * 7
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
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
        // target: 'https://keep-up-backend.vercel.app',
        // agent: new HttpsProxyAgent('http://127.0.0.1:7890'),
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
    
            // 如果是 POST/PUT 请求，添加请求体
            if (['POST', 'PUT'].includes(req.method) && req.body) {
              curlCommand += ` -d '${JSON.stringify(req.body)}'`;
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
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'article': ['marked'],
          'ui': ['element-plus']
        }
      }
    },
    sourcemap: true,
    assetsDir: 'assets'
  }
})
