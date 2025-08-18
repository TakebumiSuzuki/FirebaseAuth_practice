<script setup>
  import { reactive, ref } from 'vue'
  import { auth } from "@/firebase";
  import { signInWithEmailAndPassword  } from "firebase/auth";

  const formValues = reactive({
    email: '',
    password: ''
  })
  const errorMessage = ref(null)
  const successMessage = ref(null)

  const handleSubmit = async ()=>{
    successMessage.value = null
    errorMessage.value = null

    try{
      const userCredential = await signInWithEmailAndPassword(
        auth,
        formValues.email,
        formValues.password
      )
      // signInWithEmailAndPassword が成功して次の行に進んだ時点で、userCredential オブジェクトと、
      // その中の user プロパティは必ず存在するので if (userCredential && userCredential.user) は必要ない。

      console.log(userCredential.user)

      successMessage.value = 'Successfully you have logged in'


    }catch(error){
      // 開発者向けにエラー詳細をログ出力
      console.error("Firebase Auth Error:", error.code, error.message);

      let userMessage;

      // 【必須】ユーザーの入力に起因するエラーを個別処理
      switch (error.code) {
        case 'auth/user-not-found':
        case 'auth/wrong-password':
          userMessage = "メールアドレスまたはパスワードが正しくありません。";
          break;
        case 'auth/invalid-email':
          userMessage = "メールアドレスの形式が正しくありません。";
          break;
        case 'auth/too-many-requests': // 5. エラーケースを追加
          userMessage = "試行回数が上限を超えました。しばらくしてから再度お試しください。";
          break;
        case 'auth/network-request-failed':
          userMessage = "ネットワークに接続できませんでした。接続を確認してください。";
          break;

        // その他の予期せぬエラーをdefaultでキャッチ
        default:
          userMessage = "予期せぬエラーが発生しました。時間をおいて再度お試しください。";
          break;
      }
      errorMessage.value = userMessage
    }

  }

</script>

<template>
  <div class="px-8 max-w-[600px] mx-auto h-screen py-16 ">
    <div class="shadow-xl py-16 px-12 bg-linear-30 from-purple-200 to-sky-200 rounded-3xl">
      <h1 class="text-4xl text-center mb-8">
        Login
      </h1>

      <form @submit.prevent="handleSubmit">
        <p v-if="errorMessage" class="text-center text-red-500">{{ errorMessage }}</p>
        <p v-if="successMessage" class="text-center text-blue-500">{{ successMessage }}</p>
        <div class="mb-8">
          <label for="email" class="block mb-1">Email</label>
          <input
            id="email"
            v-model="formValues.email"
            type="email"
            class="px-4 py-2 rounded-xl  transition border-2 border-gray-400/80 w-full"
          >
        </div>

        <div class="mb-8" >
          <label for="password" class="block mb-1">Password</label>
          <input
            id="password"
            v-model="formValues.password"
            type="password"
            class="px-4 py-2 rounded-xl  transition border-2 border-gray-400/80 w-full"
          >
        </div>

        <button
          type="submit"
          class="px-8 py-2 rounded-xl hover:bg-purple-300/30 hover:-translate-y-0.5 transition border-2 border-gray-400/80"
        >
          Submit
        </button>
      </form>


    </div>
  </div>



</template>