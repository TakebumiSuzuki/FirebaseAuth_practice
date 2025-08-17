<script setup>
  import { reactive, ref } from 'vue'
  import { auth } from "@/firebase";
  import { signInWithEmailAndPassword  } from "firebase/auth";

  const formData = reactive({
    email: '',
    password: ''
  })
  const errorMessage = ref('')
  const successMessage = ref('')

  const handleSubmit = async ()=>{
    try{
      const response = await signInWithEmailAndPassword(auth, formData.email, formData.password)

      if (response && response.user){
        console.log(response.user)
      }
      successMessage.value = 'Successfully yo have logged in'
    }catch(error){
      console.error(error)
      errorMessage.value = 'Failed to log in'
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
            v-model="formData.email"
            type="email"
            class="px-8 py-2 rounded-xl hover:bg-purple-300/80 transition border-2 border-gray-400/80 w-full"
          >
        </div>

        <div class="mb-8" >
          <label for="password" class="block mb-1">Password</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            class="px-8 py-2 rounded-xl hover:bg-purple-300/80 transition border-2 border-gray-400/80 w-full"
          >
        </div>

        <button
          type="submit"
          class="px-8 py-2 rounded-xl hover:bg-purple-300/80 transition border-2 border-gray-400/80"
        >
          Submit
        </button>
      </form>


    </div>
  </div>



</template>