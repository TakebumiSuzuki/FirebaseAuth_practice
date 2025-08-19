<script setup>
  import { ref } from "vue";
  import { auth } from "@/firebase";
  import { createUserWithEmailAndPassword, updateProfile  } from "firebase/auth";
  import { apiClient } from '@/api'

  const username = ref('')
  const email = ref('');
  const password = ref('');

  const successMessage = ref(null);
  const errorMessage = ref(null);

  const register = async () => {
    successMessage.value = null;
    errorMessage.value = null;

    try {
      // 第二引数は必ずメールアドレス、第三引数は必ずパスワード
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email.value,
        password.value
      );

      // 以下のコードは FB authサーバーのユーザー情報を変えるだけで、IDトークンにはすぐ反映されない
      // 次回リフレッシュ時にこのdisplayNameがIDトークンに反映される
      await updateProfile(
        userCredential.user,
        { displayName: username.value }
      );

      await apiClient.post('/api/v1/auth/create-user-profile', { display_name : username.value })


      successMessage.value = "登録が成功しました！";
      console.log("User:", userCredential.user);

    } catch (error) {
      // 開発者向けにエラー詳細をコンソールに出力
      console.error("Firebase Auth Error:", error.code, error.message);

      let userMessage;

      // Firebaseから返されたエラーコードに応じて、ユーザーへのメッセージを分岐
      switch (error.code) {
        case 'auth/email-already-in-use':
          userMessage = "このメールアドレスは既に使用されています。";
          break;
        case 'auth/invalid-email':
          userMessage = "メールアドレスの形式が正しくありません。";
          break;
        case 'auth/weak-password':
          userMessage = "パスワードは6文字以上で設定してください。";
          break;
        case 'auth/operation-not-allowed':
          // Firebaseコンソールで認証方法が有効でない場合など
          userMessage = "現在、この登録方法はご利用いただけません。";
          break;
        default:
          userMessage = "予期せぬエラーが発生しました。時間をおいて再度お試しください。";
          break;
      }
      // 決定したエラーメッセージを画面に表示
      errorMessage.value = userMessage;
    }
  };

</script>


<template>
  <div class="px-8 max-w-[600px] mx-auto h-screen py-16 ">
    <div class="shadow-xl py-16 px-12 bg-linear-30 from-purple-200 to-sky-200 rounded-3xl">
      <h1 class="text-4xl text-center mb-8">
        Register
      </h1>
      <form @submit.prevent="register">
        <div class="mb-8">
          <label
            for="username"
            class="block mb-1"
          >Username:</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="border rounded-xl px-4 py-2 w-full"
          >
        </div>

        <div class="mb-8">
          <label
            for="email"
            class="block mb-1"
          >Email:</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="border rounded-xl px-4 py-2 w-full"
          >
        </div>

        <div class="mb-8">
          <label
            for="password"
            class="block mb-1"
          >Password:</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="border rounded-xl px-4 py-2 w-full"
          >
        </div>

        <button
          type="submit"
          class="px-8 py-2 rounded-xl hover:bg-purple-300/80 transition border-2 border-gray-400/80"
        >
          Submit
        </button>
      </form>

      <!-- 登録結果を表示する部分（任意） -->
      <div v-if="successMessage" class="mt-4 p-4 bg-green-200 text-green-800 rounded-xl">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="mt-4 p-4 bg-red-200 text-red-800 rounded-xl">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>