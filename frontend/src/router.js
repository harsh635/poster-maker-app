import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Poster from './views/Poster.vue'
import AdminLogin from './views/AdminLogin.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import UserStatistics from './views/UserStatistics.vue'
import { useUser } from './useUser'

const routes = [
  { path: '/', component: Home },
  {
    path: '/posters',
    component: Poster,
    meta: { requiresAuth: true, requiresSubscription: true }
  },
  { path: '/admin/login', component: AdminLogin },
  {
    path: '/admin/dashboard',
    component: AdminDashboard,
    meta: { adminOnly: true } // both sub & super can access
  },
  {
    path: '/admin/users',
    component: UserStatistics,
    meta: { adminOnly: true, superOnly: true } // only super
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const { user, admin } = useUser()

  const requiresAuth = to.meta.requiresAuth
  const requiresSub = to.meta.requiresSubscription

  // Allow open access to admin login page
  if (to.path === '/admin/login') {
    return next()
  }

  const isAdminRoute = to.path.startsWith('/admin')

  if (isAdminRoute) {
    if (!admin.value || !admin.value.username) {
      return next('/')  // not logged in as admin
    }

    // only super admins can access /admin/users
    if (to.path === '/admin/users' && admin.value.role !== 'super') {
      return next('/admin/dashboard')
    }

    return next()
  }

  // Normal user auth checks
  if (requiresAuth && !user.value) {
    return next('/')
  }

  if (requiresSub && !user.value?.is_subscribed) {
    return next('/')
  }

  next()
})

export default router
