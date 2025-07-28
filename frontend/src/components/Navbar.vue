<template>
  <nav class="navbar navbar-expand-lg px-3 py-2 shadow-sm custom-navbar">
    <div class="container-fluid">
      <!-- Logo -->
      <router-link to="/" class="navbar-brand d-flex align-items-center gap-2 text-white">
        <img src="/templates/Logo Johar 1.png" alt="Logo" class="logo-img" />
      </router-link>

      <!-- Toggler for mobile -->
      <button class="navbar-toggler" type="button" @click="toggleMobileMenu">
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Menu -->
      <div class="collapse navbar-collapse" :class="{ show: isMobileMenuOpen }">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-lg-center gap-lg-3 text-center flex-column flex-lg-row">
          <li class="nav-item">
            <router-link to="/" class="nav-link">Home</router-link>
          </li>
          <li class="nav-item">
            <button class="nav-link btn btn-link text-white" @click="handleAllPosters">All Posters</button>
          </li>
          <li class="nav-item">
            <router-link to="/admin/login" class="nav-link">Admin Section</router-link>
          </li>
          <li class="nav-item">
            <a href="/app-debug.apk" download class="nav-link">📱 Download App</a>
          </li>

          <!-- User Dropdown -->
          <li class="nav-item" v-if="user">
            <div class="dropdown text-center">
              <img
                :src="getFullImageUrl(user.profile_image_url) || DEFAULT_AVATAR"
                class="profile-pic"
                @click="toggleDropdown"
              />
              <transition name="fade">
                <ul v-if="showDropdown" class="dropdown-menu show">
                  <li>
                    <button class="dropdown-item" @click="logout">Logout</button>
                  </li>
                </ul>
              </transition>
            </div>
          </li>

          <!-- Login button -->
          <li class="nav-item" v-else>
            <button class="btn btn-outline-light mt-2 mt-lg-0" @click="openAuthModal('login')">Login</button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Auth Modal -->
    <AuthModal v-if="showAuth" :mode="authMode" @close="showAuth = false" @switch="toggleAuthMode" />
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineExpose  } from 'vue'
import { useRouter } from 'vue-router'
import AuthModal from './AuthModal.vue'
import  {useUser} from '../useUser'

const router = useRouter()
const showDropdown = ref(false)
const showAuth = ref(false)
const authMode = ref('login')
const DEFAULT_AVATAR = 'https://cdn-icons-png.flaticon.com/512/3177/3177440.png'
const { user, setUser } = useUser()

// Auth modal handlers
function openAuthModal(mode) {
  authMode.value = mode
  showAuth.value = true
}
function toggleAuthMode() {
  authMode.value = authMode.value === 'login' ? 'register' : 'login'
}
function logout() {
  setUser(null)
  router.push('/')
}
function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}
function getFullImageUrl(path) {
  const base = import.meta.env.VITE_API_URL || ''
  return path?.startsWith('http') ? path : `${base}${path}`
}

function handleAllPosters() {
  if (!user.value) {
    openAuthModal('login')
  } else {
    router.push('/posters')
  }
}

function loginHandler(e) {
  setUser(e.detail)
  showAuth.value = false
}

const isMobileMenuOpen = ref(false)
function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

onMounted(() => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) setUser(JSON.parse(savedUser))

  window.addEventListener('login-success', loginHandler)
})

onUnmounted(() => {
  window.removeEventListener('login-success', loginHandler)
})

// Close dropdown on outside click
document.addEventListener('click', (e) => {
  if (!e.target.closest('.dropdown')) {
    showDropdown.value = false
  }
})

// Expose modal control to parent
defineExpose({ openAuthModal, openSubscriptionModal: () => subscriptionModalRef.value?.open() })
</script>

<style scoped>
.custom-navbar {
  background-color: #39971a;
  color: white;
}

.nav-link {
  color: white !important;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #cde3d4 !important;
}

.logo-img {
  height: 42px;
  width: auto;
  object-fit: contain;
  background-color: white;           /* Contrast background */
  padding: 4px;                      /* Inner spacing */
  border-radius: 8px;                /* Rounded corners */
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2); /* Subtle shadow */
  border: 1px solid #ccc;            /* Thin border for clarity */
}


.profile-pic {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 50px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  min-width: 120px;
  z-index: 999;
  padding: 0.5rem 0;
}

.dropdown-item {
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  font-size: 0.95rem;
  cursor: pointer;
}
.dropdown-item:hover {
  background-color: #f8f9fa;
}

.btn-outline-light {
  border: 1px solid white;
  color: white;
}
.btn-outline-light:hover {
  background-color: white;
  color: #0E5D39;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .navbar-nav {
    gap: 0.5rem;
    flex-direction: column;
    align-items: center;
  }
}
</style>