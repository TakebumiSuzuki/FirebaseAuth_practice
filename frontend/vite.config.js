import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({

  plugins: [
    vue(),
    tailwindcss(),
    vueDevTools(),
  ],

  server:{
    // host: true の設定がないと、Viteサーバーはコンテナのlocalhost(127.0.0.1)でのみリッスンするため、
    // コンテナの外（ホストマシン）からアクセスすることができません。Viteは 0.0.0.0 でリッスンし、
    // Dockerのポートフォワーディングを通じて外部からのアクセスを受け付けるようになります。
    host: true,
    // 5173はデフォルトなので書かなくてもOK
    port: 5173,
    proxy: {
      // '/api' で始まるリクエストをプロキシする
      '/api': {
        // 転送先：docker-compose.ymlで定義したバックエンドサービスのURL
        target: 'http://backend:5000',

        // changeOriginの設定は、例えば、バックエンドが特定の仮想ホスト名（例: api.example.com）を期待
        // している場合や、http://localhost:3000 からのリクエストのみを許可する設定になっている場合などに、
        // ここをtrueにすると、Origin ヘッダーを target に指定したバックエンドAPIのオリジンに書き換えて
        // 転送します。つまり、オリジンを偽装してCORSエラーを回避する
        // 多くのシンプルなバックエンドAPIは、Originヘッダーをそこまで厳密にチェックしませんので、なくても良い。
        changeOrigin: true,


        // パスから '/api' を削除しない場合（Flask側で/api/xxxを想定しているなら不要）
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
