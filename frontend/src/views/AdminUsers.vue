<script setup>
import { onMounted, ref } from 'vue'
import { apiClient } from '@/api';
// import auth from 'firebase/auth'

const users = ref(null)


onMounted(async ()=>{
  try{
    // const { data: {users, nextPageToken} } = await apiClient.get('/api/v1/admin/users')
    const response = await apiClient.get('/api/v1/admin/users')
    users.value = response.data['users']


  }catch(err){
    console.log('エラーです', err)
  }
})

const handleDisabled = async(uid)=>{
  try{
    console.log(uid)
    const response = await apiClient.post('api/v1/admin/users/change-disable',{ uid })
    console.log(response.data.disabled)

  }catch(error){
    console.log('errrです')
  }


}
const handleAdminState = async(uid)=>{
  try{
    console.log(uid)
    const response = await apiClient.post('api/v1/admin/users/change-role',{ uid })
    console.log(response.data)
  }catch(error){
    console.log('errrです')

  }
}

</script>

<template>
  <div class="px-4 md:px-8 py-8">
    <div class="py-8 max-w-[900px] mx-auto border">
      <h1 class="text-5xl text-center">USERS</h1>

      <div class="my-8">
        <div v-for="user in users" :key="user.uid">
          <div class="py-4">
            <p>{{ user.uid }}</p>
            <p>{{ user.email }}</p>
            <p>{{ user.display_name }}</p>

            <div class="flex items-center gap-2">
              <input :id="`disabled-${user.uid}`" type="checkbox"
                @change="handleDisabled(user.uid)">
              <label :for="`disabled-${user.uid}`">Disabled</label>
            </div>

            <div class="flex items-center gap-2">
              <input :id="`admin-${user.uid}`" type="checkbox"
                checked="!!user.custom_claims?.is_admin || false"
                @change="handleAdminState(user.uid)"
              >
              <label :for="`admin-${user.uid}`" >Admin</label>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>


</template>