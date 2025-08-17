<script setup>
  import { ref } from "vue";
  import { auth } from "@/firebase";
  import { createUserWithEmailAndPassword, updateProfile  } from "firebase/auth";

  const username = ref('')
  const email = ref('');
  const password = ref('');

  const errorMessage = ref('');
  const successMessage = ref('');

  const register = async () => {
    errorMessage.value = '';
    successMessage.value = '';

    try {
      // 第二引数は必ずメールアドレス、第三引数は必ずパスワード
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email.value,
        password.value
      );

      await updateProfile(userCredential.user, {
        displayName: username.value
      });
      successMessage.value = "登録が成功しました！";
      console.log("User:", userCredential.user);
    } catch (error) {
      errorMessage.value = error.message;
      console.error(error);
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