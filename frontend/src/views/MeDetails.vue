<script setup>
import { onMounted } from 'vue'
import { apiClient } from '@/api'
import { useAuthStore } from '@/stores/useAuthStore'

const authStore = useAuthStore()

onMounted(async()=>{
  try{
    const response = await apiClient.get('/api/v1/users/me')
    console.log(response.data)
  }catch(error){
    console.log('情報取得に失敗しました')
  }
})
</script>

<template>
  Me Details
</template>