<template>
  <nav class="navbar navbar-expand-lg bg-light px-4 py-3 shadow-sm">
    <div class="container-fluid fw-bold d-flex justify-content-between align-items-center">
      <router-link to="/admin/dashboard" class="navbar-brand">🛠 Admin Panel</router-link>

      <div class="d-flex align-items-center gap-3">
        <router-link to="/admin/dashboard" class="nav-link px-2">Dashboard</router-link>
        <router-link v-if="isSuperAdmin" to="/admin/users" class="nav-link px-2">User Statistics</router-link>

        <!-- Profile Dropdown -->
        <div class="dropdown position-relative" v-if="admin">
          <img
            :src="DEFAULT_AVATAR"
            class="profile-pic"
            @click="toggleDropdown"
          />
          <transition name="fade">
            <ul v-if="showDropdown" class="dropdown-menu show">
              <li><button class="dropdown-item" @click="logout">Logout</button></li>
            </ul>
          </transition>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '../useUser'

const router = useRouter()
const showDropdown = ref(false)
const DEFAULT_AVATAR = 'https://cdn-icons-png.flaticon.com/512/3177/3177440.png'
const { admin, setAdmin } = useUser()


// Helpers
const isSuperAdmin = computed(() => admin.value?.role === 'super')

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function logout() {
  setAdmin(null) 
  router.push('/')
}

function getFullImageUrl(path) {
  const base = import.meta.env.VITE_API_URL || ''
  return path?.startsWith('http') ? path : `${base}${path}`
}

// Close dropdown on outside click
document.addEventListener('click', (e) => {
  if (!e.target.closest('.dropdown')) {
    showDropdown.value = false
  }
})
</script>

<style scoped>
.nav-link {
  font-weight: 500;
}

.profile-pic {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #007bff;
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

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

</style>
