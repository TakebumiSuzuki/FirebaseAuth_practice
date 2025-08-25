import { createApp } from 'vue'
import App from '@/App.vue'
import { createPinia } from 'pinia'
// auth オブジェクトがインポートされた時点で、Firebase Auth が自動的に以下を非同期で行います：
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

auth.onAuthStateChanged(async (user) => {
  const authStore = useAuthStore()
  await authStore.setUser(user)

  // ログインやログアウトの時には、既に isAppMounted は true になっている
  if (!isAppMounted) {
    app.mount('#app')
    isAppMounted = true
  }
})
