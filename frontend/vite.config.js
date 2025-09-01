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
    // しかし、Dockerfileの方に、CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]と
    // 記述しており、こちらの方が優先されるので、この vite.config に host:true を書くのは冗長
    // host: true,
    // 5173はデフォルトなので書かなくてもOK
    // port: 5173,
    proxy: {
      // '/api' で始まるリクエストをプロキシする。つまり、クライアントからviteサーバーに届いた
      // リクエストを中継してbackendの方に送る
      '/api': {
        // 転送先：docker-compose.ymlで定義したバックエンドサービスのURL
        target: 'http://backend:5000',

        // changeOriginの設定は、例えば、バックエンドが特定の仮想ホスト名（例: api.example.com）を期待
        // している場合や、http://localhost:3000 からのリクエストのみを許可する設定になっている場合などに、
        // ここをtrueにすると、Origin ヘッダーを target に指定したバックエンドAPIのオリジンに書き換えて
        // 転送します。つまり、オリジンを偽装してCORSエラーを回避する
        // 多くのシンプルなバックエンドAPIは、Originヘッダーをそこまで厳密にチェックしませんので、なくても良い。
        // changeOrigin: true,


        // パスから '/api' を削除しない場合（Flask側で/api/xxxを想定しているなら不要）
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },

  // import.metaはECMAScript（ES）モジュールの仕様に含まれる、標準的なJavaScriptの構文
  // 現在実行されているモジュールに関するメタデータ（付加的な情報）を格納するためのオブジェクト
  // import.meta.urlで、設定ファイル（vite.config.js）自体の絶対URLを取得
  // new URL('./src', import.meta.url) は、その vite.config.js のURLを基準にして、
  // ./src という相対パスを解決した結果得られる、src ディレクトリの絶対URL
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
