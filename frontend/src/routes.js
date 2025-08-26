
import { createRouter, createWebHistory } from 'vue-router'
import AdminUsers from '@/views/AdminUsers.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import MeDetails from '@/views/MeDetails.vue'

const routes = [

  {
    path:'/admin-users',
    name: 'admin-users',
    component: AdminUsers,
    meta: {}
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
    path: '/',
    name: 'me-details',
    component: MeDetails,
    meta: {}
  }


]

const router = createRouter({
  // BASE_URLは、vite.config.js内の、base: の設定値。デフォルトは '/'になっている。　
  // 結局のところ、import.meta.env.BASE_URL の部分はルーティングの基準パス（ベースパス）を決める。　
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})


export default router;