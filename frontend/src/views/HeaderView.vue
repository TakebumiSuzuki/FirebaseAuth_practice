<script setup>
  import { ref } from 'vue'
  import { auth } from "@/firebase";
  import { signOut } from "firebase/auth"
  import { useAuthStore } from '@/stores/useAuthStore'
  import { useRouter } from 'vue-router';
  // import axios from "axios"

  const router = useRouter()
  const authStore = ref(null)

  authStore.value = useAuthStore()

  const handleLogout = async()=>{
    try {
      // await axios.post('/api/v1/auth/revoke-refresh-token')

      // signOut関数はAuthサーバーにリクエストを送らず、クライアントサイドだけで完結する処理
      // GmailやNetflixはこれだけでログアウトとしている。
      await signOut(auth);
      router.push("login");

    } catch (error) {
      console.error("ログアウトエラー:", error);

      if (error.response?.status === 401) {
        // post('/api/v1/auth/revoke-refresh-token') で失敗した場合。クライアント側のみログアウト
        console.log("認証が無効のため、クライアント側のみログアウトします");
        await signOut(auth);

      } else {
        // その他のエラーは何もせず、もう一度、ユーザーにログアウトをしてもらうメッセージを表示
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
        <p v-else-if="authStore?.isLoggedin">こんにちは一般ユーザーさん</p>
        <p v-else >あなたはログインしてません</p>
        <button
          type="button"
          class="hover:cursor-pointer"
          @click="handleLogout"
        >
          Logout
        </button>

      </div>

    </div>
  </header>
</template>