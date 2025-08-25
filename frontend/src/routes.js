
import { createRouter, createWebHistory } from 'vue-router'
import AdminUsers from '@/views/AdminUsers.vue'

const routes = [

  {
    path:'/admin-users',
    name: 'admin-users',
    component: AdminUsers,
    meta: {}
  },

]

const router = createRouter({
  // BASE_URLは、vite.config.js内の、base: の設定値。デフォルトは '/'になっている。　
  // 結局のところ、import.meta.env.BASE_URL の部分はルーティングの基準パス（ベースパス）を決める。　
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})


export default router;