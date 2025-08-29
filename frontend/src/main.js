import { createApp } from 'vue'
// import されているすべての関連ファイル（ヘッダーコンポーネントなど）のコードがメモリに読み込まれます
// しかし設計図（定義）を読み込んでいるだけで、<script setup> の中のコードはまだ実行されません。
import App from '@/App.vue'
import { createPinia } from 'pinia'
// auth オブジェクトがインポートされた時点で、Firebase Auth が自動的に以下を'非同期で'行います：
// Firebase Auth サーバーとの接続を確立
// ブラウザの認証状態（localStorage、sessionStorage など）をチェック。
// 認証状態が確認できた時点で onAuthStateChanged コールバックを自動実行
// つまり、onAuthStateChanged を登録した瞬間に、すでに Firebase が認証状態をチェックして、その結果をコールバックに渡してくれます。
// 非同期なので、これら認証の確認を任せつつ、まず、このjsファイルの最後まで同期的に貫徹する。
import { auth } from '@/firebase'
import  { useAuthStore } from '@/stores/useAuthStore'
import router from '@/routes'

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)
app.use(router)


let isAppMounted = false

// サインイン済みなら user にユーザー情報が渡される、未サインインなら user = null が渡される
// また、同じタイミングで、auth.currentUser にも同じ値が代入される。
auth.onAuthStateChanged(async (user) => {
  const authStore = useAuthStore()
  await authStore.setUser(user)

  // ユーザーがログインやログアウトをするシチュエーションでは、既に isAppMounted は true になっている
  if (!isAppMounted) {
    app.mount('#app')
    isAppMounted = true
  }
})
