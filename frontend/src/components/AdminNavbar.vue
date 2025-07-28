<template>
  <nav class="navbar navbar-expand-lg bg-light px-3 py-3 shadow-sm">
    <div class="container-fluid fw-bold">
      <router-link to="/admin/dashboard" class="navbar-brand">🛠 Admin Panel</router-link>

      <!-- Hamburger Toggle Button -->
      <button
        class="navbar-toggler"
        type="button"
        @click="toggleCollapse"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Collapsible Content -->
      <div class="collapse navbar-collapse" :class="{ show: isCollapsed }">
        <ul class="navbar-nav ms-auto align-items-center gap-lg-3 gap-2">
          <li class="nav-item">
            <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="isSuperAdmin">
            <router-link to="/admin/users" class="nav-link">User Statistics</router-link>
          </li>
          <li class="nav-item dropdown" v-if="admin">
            <img
              :src="DEFAULT_AVATAR"
              class="profile-pic"
              @click="toggleDropdown"
            />
            <transition name="fade">
              <ul v-if="showDropdown" class="dropdown-menu show mt-2">
                <li><button class="dropdown-item" @click="logout">Logout</button></li>
              </ul>
            </transition>
          </li>
        </ul>
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

const isCollapsed = ref(false)

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

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

/* Bootstrap hamburger icon fallback */
.navbar-toggler {
  border: none;
  background: transparent;
}
.navbar-toggler-icon {
  display: inline-block;
  width: 24px;
  height: 2px;
  background-color: #333;
  position: relative;
}
.navbar-toggler-icon::before,
.navbar-toggler-icon::after {
  content: "";
  position: absolute;
  width: 24px;
  height: 2px;
  background-color: #333;
  left: 0;
}
.navbar-toggler-icon::before {
  top: -8px;
}
.navbar-toggler-icon::after {
  top: 8px;
}

/* Dropdown */
.dropdown-menu {
  position: absolute;
  right: 0;
  top: 60px;
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

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive Tweaks */
@media (max-width: 768px) {
  .navbar-nav {
    flex-direction: column;
    align-items: flex-start !important;
    padding-top: 1rem;
  }

  .navbar-nav .nav-item {
    width: 100%;
  }

  .navbar-nav .nav-link {
    width: 100%;
    padding: 0.5rem 0;
  }

  .dropdown-menu {
    top: auto;
    position: relative;
    box-shadow: none;
    border: none;
    padding-left: 0.5rem;
  }

  .profile-pic {
    margin-top: 0.5rem;
  }
}


</style>
