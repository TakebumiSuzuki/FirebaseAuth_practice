<script setup>
import { onMounted, ref } from 'vue'
import { apiClient } from '@/api'
import { useAuthStore } from '@/stores/useAuthStore'
import { useRouter } from 'vue-router'
import { formatDateToYMD } from '@/utils'

const authStore = useAuthStore()
const meData = ref(null)
const router = useRouter()

onMounted(async()=>{
  try{
    const response = await apiClient.get('/api/v1/users/me')
    meData.value = response.data

  }catch(error){
    console.log('情報取得に失敗しました', error)
  }
})

const handleDeleteMe = async ()=>{
  try{
    const response = await apiClient.delete('/api/v1/users/me')
    router.push({name: 'login'})
  }catch(error){
    console.log('Me削除に失敗しました')
  }
}

</script>

<template>
  <div class="px-4 md:px-8 py-8">
    <div class="w-full max-w-[600px] mx-auto border rounded-xl py-4 px-10">
      <h1 class="text-4xl text-center">YOUR INFORMATION</h1>
      <div v-if="meData">
        <div v-for="[key, value] in Object.entries(meData)" class="my-4">
          <p class="font-semibold underline">{{ key }}:</p>
          <p>{{ value || 'N/A' }}</p>
        </div>
      </div>
      <div class="space-y-4">
        <RouterLink :to="{name: 'me-update'}" class="w-full block px-4 py-2 border rounded-xl text-center hover:bg-gray-200">
          Edit Info
        </RouterLink>

        <button type="button" class="w-full block px-4 py-2 border rounded-xl text-center hover:bg-gray-200" @click="handleDeleteMe">
          Delete My Account
        </button>
      </div>
    </div>
  </div>
</template>