// useUser.js
import { ref } from 'vue'

// Singleton refs (global across app)
const user = ref(JSON.parse(localStorage.getItem('user')) || null)
const admin = ref(JSON.parse(localStorage.getItem('admin')) || null)

function setUser(updatedUser) {
  user.value = updatedUser
  if (updatedUser) {
    localStorage.setItem('user', JSON.stringify(updatedUser))
  } else {
    localStorage.removeItem('user')
  }
}

function setAdmin(updatedAdmin) {
  admin.value = updatedAdmin
  if (updatedAdmin) {
    localStorage.setItem('admin', JSON.stringify(updatedAdmin))
  } else {
    localStorage.removeItem('admin')
  }
}

export function useUser() {

  return {
    user,
    admin,
    setUser,
    setAdmin
  }
}
