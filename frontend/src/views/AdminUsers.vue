<script setup>
import { onMounted, ref, reactive } from 'vue'
import { apiClient } from '@/api';

const users = ref(null)
const loadingStates = reactive({})

const isLoading = (uid) => {
  const state = loadingStates[uid];
  if (!state) return false;
  return state.admin || state.disabled || state.delete;
}

const fetchUsers = async()=>{
  try{
    const response = await apiClient.get('/api/v1/admin/users')
    users.value = response.data['users']
  }catch(error){
    console.log('ユーザーリストの情報取得に失敗しました', error)
    // Notification (もう少し時間を置いてリロードしてください)
  }
}

onMounted(async ()=>{
  await fetchUsers()
  if (users.value){
    for(let user of users.value){
      loadingStates[user.uid] = {'disabled': false, 'admin': false, 'delete': false}
    }
  }
})

const handleDisabled = async(uid)=>{
  try{
    console.log(uid)
    loadingStates[uid].disabled = true
    const response = await apiClient.post('/api/v1/admin/users/change-disabled',{ uid })
    console.log(response.data.disabled)
    await fetchUsers()
  }catch(error){
    console.log('errrです')
  }finally{
    loadingStates[uid].disabled = false
  }
}

const handleAdminState = async(uid)=>{
  try{
    console.log(uid)
    loadingStates[uid].admin = true
    const response = await apiClient.post('/api/v1/admin/users/change-role',{ uid })
    console.log(response.data)
    await fetchUsers()
  }catch(error){
    console.log('errrです')
  }finally{
    loadingStates[uid].admin = false
  }
}

const handleDeleteUser = async(uid)=>{
  try{
    console.log(uid)
    loadingStates[uid].delete = true
    // deleteメソッドだと、payloadに情報をいれられず、第二引数はconfigになってしまう。なのでpostを使うことに。
    await apiClient.post('/api/v1/admin/users/delete-user', {uid})
    console.log('deleteしました')
    // Notification (Delete成功)
    await fetchUsers()
  }catch(error){
    console.log('deleteに失敗しました。', error)
    // Notification (Delete失敗、もう一度ボタンを押してください。)
    return
  }finally{
    loadingStates[uid].delete = false
  }
}
</script>

<template>
  <div class="px-4 md:px-8 py-8">
    <div class="py-8 max-w-[900px] mx-auto border">
      <h1 class="text-5xl text-center">USERS</h1>

      <div class="my-8">
        <div v-for="user in users" :key="user.uid" >
          <RouterLink
            :to="{name: 'admin-user-details', params: {uid: user.uid}}"
            class="relative py-1 bg-gray-300 my-1 block"
          >
            <p>{{ user.uid }}</p>
            <p>{{ user.email }}</p>
            <p>{{ user.display_name }}</p>

            <div class="flex items-center gap-2">
              <input :id="`disabled-${user.uid}`"
                type="checkbox"
                :checked="user.disabled"
                @click.stop
                @change="handleDisabled(user.uid)"
              >
              <label :for="`disabled-${user.uid}`" @click.stop>Disabled</label>
            </div>

            <div class="flex items-center gap-2">
              <input :id="`admin-${user.uid}`"
                :checked="user.custom_claims?.is_admin || false"
                type="checkbox"
                @click.stop
                @change.stop="handleAdminState(user.uid)"
              >
              <label :for="`admin-${user.uid}`" @click.stop>Admin</label>
            </div>

            <button
              type="button"
              class="px-3 py-0.5 rounded-lg bg-purple-300 hover:cursor-pointer"
              @click.stop="handleDeleteUser(user.uid)">
              Delete
            </button>

            <div
              v-if="isLoading(user.uid)"
              class="absolute inset-0 bg-red-300/40"
            >
            </div>

          </RouterLink>
        </div>
      </div>
    </div>
  </div>


</template>