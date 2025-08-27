<script setup>
  import { onMounted, ref } from 'vue'
  import { apiClient } from '@/api'

  const props = defineProps({
    uid: { type: String, required: true}
  })

  const user = ref(null)

  onMounted(async()=>{
    try{
      const response = await apiClient.get(`/api/v1/admin/users/${props.uid}`)
      user.value = response.data
      console.log(user.value)
      
    }catch(error){
      console.log('失敗')
    }
  })


</script>

<template>
  <h1>User Data</h1>
  <div v-if="user">{{user.uid}}
    <div v-for="([key, value]) in Object.entries(user)" :key="key" class="my-4">
      <p>{{ key }}</p>
      <p>{{ value || 'N/A'}}</p>
    </div>
  </div>
</template>