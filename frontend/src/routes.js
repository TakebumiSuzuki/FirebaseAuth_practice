import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '@/firebase'

import AdminUsers from '@/views/AdminUsers.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import MeDetails from '@/views/MeDetails.vue'
import AdminUserDetails from '@/views/AdminUserDetails.vue'
import MeUpdate from '@/views/MeUpdate.vue'
import ForbiddenView from '@/views/ForbiddenView.vue'

const routes = [

  {
    path:'/admin-users',
    name: 'admin-users',
    component: AdminUsers,
    meta: { 'admin_required': true }
  },
  {
    path:'/admin-user-details/:uid',
    name: 'admin-user-details',
    component: AdminUserDetails,
    props: true,
    meta:  { 'admin_required': true }
  },
  {
    path: '/auth/register',
    name: 'register',
    component: RegisterView,
    meta: {}
  },
  {
    path: '/auth/login',
    name: 'login',
    component: LoginView,
    meta: {}

  },
  {
    path: '/users/me',
    name: 'me-details',
    component: MeDetails,
    meta: {'login_required': true}
  },
  {
    path: '/users/me-update',
    name: 'me-update',
    component: MeUpdate,
    meta: {'login_required': true}
  },
  {
    path: '/forbidden',
    name: 'forbidden',
    component: ForbiddenView,
  }

]

const router = createRouter({
  // BASE_URLは、vite.config.js内の、base: の設定値。デフォルトは '/'になっている。　
  // 結局のところ、import.meta.env.BASE_URL の部分はルーティングの基準パス（ベースパス）を決める。　
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})


router.beforeEach(async (to, from)=>{
  const user = auth.currentUser

  if (to.meta.login_required){
    if (!user){
      return {name: 'login'}
    }
    try{
      const idTokenResult = await user.getIdTokenResult(true)
      if (!idTokenResult){
        return {name: 'login'}
      }
    }catch(error){
      return {name: 'login'}
    }
  }


  if (to.meta.admin_required){
    if (!user){
      return {name: 'login'}
    }
    try{
      const idTokenResult = await user.getIdTokenResult(true)
      if (idTokenResult?.claims?.is_admin){
        return true
      }else{
        return {name: 'forbidden'}
      }
    }catch(error){
      return {name: 'forbidden'}
    }

  }

  return true
})


export default router;