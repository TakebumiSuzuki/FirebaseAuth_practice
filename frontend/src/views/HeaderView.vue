<script setup>
  import { onMounted, ref } from 'vue'
  import { auth } from "@/firebase";
  import { signOut } from "firebase/auth"
  import { useAuthStore } from '@/stores/useAuthStore'
  // import axios from "axios"


  // authStoreを宣言
  const authStore = ref(null)

  onMounted(() => {
    // コンポーネントがマウントされてからストアを取得
    authStore.value = useAuthStore()
  })

  const handleLogout = async()=>{
    try {
      await axios.post('/api/v1/auth/revoke-refresh-token')

      // signOut関数はAuthサーバーにリクエストを送らず、クライアントサイドだけで完結する処理
      // GmailやNetflixはこれだけでログアウトとしている。
      await signOut(auth);


      console.log("ログアウトしました");
      // ログアウト後にログインページなどにリダイレクト
      // router.push("/login");
    } catch (error) {
      console.error("ログアウトエラー:", error);

      // エラーの種類に応じた処理
      if (error.response?.status === 401) {
        // 認証エラーの場合はクライアント側もログアウト
        console.log("認証が無効のため、クライアント側のみログアウトします");
        await signOut(auth);
      } else {
        // その他のエラーは再試行可能な状態を維持
        alert("ログアウトに失敗しました。ネットワークを確認して再度お試しください。");
      }
    }
  }


</script>

<template>
  <header class="h-[80px] px-8 bg-neutral-200">
    <div class="flex justify-between items-center h-full">
      <h1 class="text-4xl">Site Title</h1>
      <div class="flex itmes-center gap-6">
        <p v-if="authStore?.isAdmin">こんにちは管理者さん</p>
        <p v-else>こんにちは一般ユーザーさん</p>
        <button type="button" @click="handleLogout">
          LOGOUT
        </button>

      </div>
    </div>

  </header>


</template>