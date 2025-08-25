<script setup>
import { onMounted } from 'vue'
import { apiClient } from '@/api';

onMounted(async ()=>{
  try{
    // const { data: {users, nextPageToken} } = await apiClient.get('/api/v1/admin/users')
    const response = await apiClient.get('/api/v1/admin/users')
    console.log(response.data)


  }catch(err){
    console.log('エラーです', err)
  }


})



</script>

<template>
  testefe


</template>