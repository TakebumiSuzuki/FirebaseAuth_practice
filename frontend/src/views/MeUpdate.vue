<script setup>
import { onMounted, ref, reactive, watch } from 'vue'
import { apiClient } from '@/api'
import { useAuthStore } from '@/stores/useAuthStore'
import { useRouter } from 'vue-router'
import { formatDateToYMD } from '@/utils'

const authStore = useAuthStore()
const router = useRouter()
const inputData = reactive({
  display_name: '',
  birthday: '',
  gender: 'male',
})

let originalData = {}

watch(inputData, (newInputData)=>{
  console.log(newInputData)
})

onMounted(async()=>{
  try{
    const response = await apiClient.get('/api/v1/users/me')
    inputData.display_name = response.data.display_name
    inputData.birthday = formatDateToYMD(response.data.birthday)
    inputData.gender = response.data.gender
    originalData = { ...inputData }
  }catch(error){
    console.log('情報取得に失敗しました', error)
  }
})

const handleUpdateData = async ()=>{
  let updates = {}
  for (const [key, value] of Object.entries(originalData)){
    if (originalData[key] !== inputData[key]){
      console.log(key)
      updates[key] = inputData[key]
    }
  }
  if (Object.keys(updates).length === 0)  return;
  console.log(updates)
  try{
    const response = await apiClient.patch('/api/v1/users/me', updates)
    console.log('3')
    console.log('保存成功')
    router.push({name:'me-details'})

  }catch(error){
    console.error('保存失敗', error)
  }
}

</script>

<template>
  <div class="px-4 md:px-8 py-8">
    <div class="w-full max-w-[600px] mx-auto border rounded-xl py-10 px-10">
      <h1 class="text-4xl text-center">UPDATE YOUR DATA</h1>
      <form class="space-y-8 mt-8">
        <div>
          <label for="display-name" class="block">Name:</label>
          <input
            id="display-name"
            v-model="inputData.display_name"
            type="text"
            class="w-full block border rounded-lg px-4 py-2"
          >
        </div>

        <div>
          <label for="birthday" class="block">Birthday:</label>
          <input
            id="birthday"
            v-model="inputData.birthday"
            type="date"
            class="border py-2 px-4 rounded-lg"
          >
        </div>

        <div>
          <p>Gender:</p>
          <div>
            <input
              id="male"
              v-model="inputData.gender"
              type="radio"
              name="gender"
              value="male"
            >
            <label for="male" class="ml-2">Male</label>
          </div>
          <div>
            <input
              id="female"
              v-model="inputData.gender"
              type="radio"
              name="gender"
              value="female"
            >
            <label for="female" class="ml-2">Female</label>
          </div>
          <div>
            <input
              id="other"
              v-model="inputData.gender"
              type="radio"
              name="gender"
              value="other"
            >
            <label for="other" class="ml-2">Other</label>
          </div>
        </div>

        <div>
          <button
            type="button"
            class="w-full block px-4 py-2 border rounded-xl text-center hover:bg-gray-200"
            @click="handleUpdateData"
          >
            Update data
          </button>
        </div>

        <RouterLink
            :to="{ name:'me-details' }"
            type="submit"
            class="w-full block px-4 py-2 border rounded-xl text-center hover:bg-gray-200"
          >
            Cancel
          </RouterLink>

      </form>
    </div>
  </div>
</template>