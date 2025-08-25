<script setup>
import { onMounted } from 'vue'
import { apiClient } from '@/api';

onMounted(()=>{
  try{
    const { users, nextPageToken } = apiClient.get('/api/v1/admin/users')
    console.log(users)


  }catch(err){
    console.log('エラーです')
  }


})



</script>

<template>
  test


</template>