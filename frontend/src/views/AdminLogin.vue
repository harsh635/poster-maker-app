<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100 bg-light">
    <div class="card shadow p-4" style="width: 400px">
      <h4 class="text-center mb-4">🔐 Admin Login</h4>
      <input v-model="username" class="form-control mb-3" placeholder="Username" />
      <input v-model="password" type="password" class="form-control mb-3" placeholder="Password" />
      <button class="btn btn-primary w-100" @click="login">Login</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick  } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import { useUser } from '../useUser'

const router = useRouter()
const username = ref('')
const password = ref('')
const { setAdmin } = useUser()

async function login() {
  try {
    const response= await axios.post(`${import.meta.env.VITE_API_URL}/admin/login`, {
      username: username.value,
      password: password.value
    })
    
    const { username: u, role } = response.data
    const adminData = { username: u, role }

    setAdmin(adminData)

    await nextTick()
  toast.success('Login successful!', {
    autoClose: 2500,
  })

  setTimeout(() => {
    router.push('/admin/dashboard')
  }, 1000)
  }
   catch (err) {
    toast.error('Invalid credentials')
  }
}
</script>

<style scoped>
input::placeholder {
  font-size: 0.95rem;
}
</style>
