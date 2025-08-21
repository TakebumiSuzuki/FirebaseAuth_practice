<script setup>
  import { ref } from "vue";
  import { auth } from "@/firebase";
  import { createUserWithEmailAndPassword, updateProfile, deleteUser } from "firebase/auth";
  import { apiClient } from '@/api'

  const username = ref('')
  const email = ref('');
  const password = ref('');

  const successMessage = ref(null);
  const errorMessage = ref(null);

  const register = async () => {
    successMessage.value = null;
    errorMessage.value = null;
    let userCredential = null;

    // ステップ1: Firebase Authenticationでユーザーを作成
    try {
      userCredential = await createUserWithEmailAndPassword(
        auth,
        email.value,
        password.value
      );
    } catch (error) {
      console.error("Firebase Auth Error:", error.code, error.message);
      let userMessage;
      switch (error.code) {
        case 'auth/email-already-in-use':
          userMessage = "This email address is already in use.";
          break;
        case 'auth/invalid-email':
          userMessage = "The email address is not validly formatted.";
          break;
        case 'auth/weak-password':
          userMessage = "The password must be at least 6 characters long.";
          break;
        case 'auth/operation-not-allowed':
          userMessage = "This registration method is currently not available.";
          break;
        default:
          userMessage = "An unexpected error occurred. Please try again later.";
          break;
      }
      errorMessage.value = userMessage;
      return;
    }

    // ステップ2: Firebaseプロファイルの更新とバックエンドでのユーザープロファイル作成
    try {
      // 以下のコードは FB authサーバーのユーザー情報を変えるだけで、
      // IDトークンにはすぐ反映されない。次回リフレッシュ時にこのdisplayNameがIDトークンに反映される
      await updateProfile(
        userCredential.user,
        { displayName: username.value }
      );
      await apiClient.post(
        '/api/v1/auth/create-user-profile',
        { display_name: username.value }
      );
      successMessage.value = "Registration successful!";
      console.log("User registered successfully:", userCredential.user);

    } catch (error) {
      console.error("Post-registration process failed:", error);

      // 後続の処理が失敗したため、作成したFirebaseユーザーのロールバックを試みる
      if (userCredential) {
        try {
          await deleteUser(userCredential.user);
          console.log("Successfully deleted Firebase user due to registration rollback.");
        } catch (deleteError) {
          // これは重大なエラー。Authにはユーザーが存在するがバックエンドには存在せず、クリーンアップにも失敗した状態
          console.error("CRITICAL: Failed to delete Firebase user after a registration failure.", deleteError);
          errorMessage.value = "A critical error occurred during registration cleanup. Please contact support.";
          return; // 処理を中断
        }
      }

      // 発生したエラーに応じて、より具体的なエラーメッセージをユーザーに提供する
      // エラーがAxios（バックエンドAPI）からのものかチェック
      if (error.response && error.response.data) {
        errorMessage.value = `Failed to create your profile: ${error.response.data.message || 'Please try again.'}`;
      } else if (error.code) { // Firebaseのエラーかチェック (例: updateProfile)
        errorMessage.value = "Failed to update your profile information. The registration has been cancelled.";
      } else {
        // ネットワーク問題やその他の予期せぬエラーに対する汎用的なフォールバック
        errorMessage.value = "An unexpected error occurred after creating your account. The registration has been cancelled.";
      }
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