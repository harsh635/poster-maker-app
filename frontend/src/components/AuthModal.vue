<template>
  <div class="modal-overlay">
    <div class="modal-box">
      <div class="left-panel">
        <img src="/templates/Banner Johar.png" alt="Auth illustration" />
      </div>
      <div class="right-panel">
        <button class="close-btn" @click="$emit('close')">✕</button>
        <h2>{{ mode === 'login' ? 'Login' : 'Register' }}</h2>
        <form @submit.prevent="onSubmit">
          <template v-if="mode === 'register'">
            <input type="text" v-model="form.name" class="form-control mb-2" placeholder="Full Name" required />
            <input type="text" v-model="form.address" class="form-control mb-2" placeholder="Address" required />
            <input type="text" v-model="form.post" class="form-control mb-2" placeholder="Post/Position" required />
            <input type="text" v-model="form.description" class="form-control mb-2" placeholder="Description" required />
            <input type="number" v-model="form.mobile" class="form-control mb-2" placeholder="Mobile No." required />
            <label class="form-label fw-semibold">Upload Profile Photo</label>
            <input type="file" @change="onImageChange" class="form-control mb-2" accept="image/*" required/>
          </template>
          <input type="email" v-model="form.email" class="form-control mb-2" placeholder="Email" required />
          <input type="password" v-model="form.password" class="form-control mb-2" placeholder="Password" required />
          <button type="submit">{{ mode === 'login' ? 'Login' : 'Register' }}</button>
        </form>
        <p @click="$emit('switch')">
          {{ mode === 'login' ? "Don't have an account? Register" : "Have an account? Login" }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { toast } from 'vue3-toastify'
import { useUser } from '../useUser'

const { setUser } = useUser()
const props = defineProps({ mode: String })
const emit = defineEmits(['close', 'switch'])

const form = ref({ name: '', address: '', post: '', description: '', mobile: '', email: '', password: '', imageFile: null })

function onImageChange(e) { form.value.imageFile = e.target.files[0] }

async function onSubmit() {
  try {
    if (props.mode === 'login') {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, {
        email: form.value.email,
        password: form.value.password
      })
      localStorage.setItem('user', JSON.stringify(res.data.user))
      window.dispatchEvent(new CustomEvent('login-success', { detail: res.data.user  }))
      setUser(res.data.user)
      toast.success('Login successfull')

    } else {
      const data = new FormData()
      Object.entries(form.value).forEach(([k, v]) => {
      if (k === 'imageFile' && v) {
      data.append('image', v)  
      } else if (v) {
      data.append(k, v)
      }
      })
      console.log("Form being submitted:", form.value)
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/register`, data)
      setTimeout(() => {
      toast.success('Registration successful! Please login.')

      }, 100)
      emit('switch') 
    
    }
  } catch (err) {
   const msg = err.response?.data?.detail || err.response?.data?.message || 'Something went wrong!'
    if (msg.includes('User already exists')) {
      toast.error('User already registered with this email!')
    } else if (msg.includes('Unsupported file format')) {
      toast.error('Unsupported image format! Use jpg, png, jpeg, or webp.')
    } else if (msg.includes('Invalid credentials')) {
      toast.error('Invalid login credentials. Please try again.')
    } else if (msg.includes('Too many login attempts')) {
      toast.warning('Too many attempts. Please try again later.')
    } else {
      toast.error(`${msg}`)
    }
  }
}
</script>

<style scoped>

form input.form-control {
  height: 38px; /* Reduced height */
  font-size: 0.95rem;
  border-radius: 8px;
  border: 1px solid #ced4da;
  padding: 6px 10px;
  transition: border-color 0.3s ease-in-out;
  margin-bottom: 12px;
}
form input.form-control:focus {
  border-color: #0d6efd;
  outline: none;
  box-shadow: 0 0 0 2px rgba(13,110,253,0.25);
}

form .form-label {
  margin-bottom: 1px; 
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}


.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(10, 10, 10, 0.2); 
  backdrop-filter: blur(8px);        
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}


.modal-box {
  display: flex;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  max-width: 850px;
  width: 95%;
  max-height: 90vh;
  z-index: 1060;
}

.left-panel {
  flex: 1;
  background: #f4f6f8;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.left-panel img {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 10px;
}

.right-panel {
  flex: 1;
  padding: 2rem 2rem 2.5rem;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  overflow-y: auto;
}

.right-panel h2 {
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

form input[type="text"],
form input[type="email"],
form input[type="password"],
form input[type="file"] {
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

form input:focus {
  outline: none;
  border-color: #007bff;
}

form button {
  padding: 10px 16px;
  background-color: #0E5D39;
  color: white;
  transition: background-color 0.3s ease;
  font-weight: 600;
  font-size: 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

form button:hover {
  background-color: #0056b3;
}

p {
  margin-top: 1rem;
  font-size: 0.95rem;
  color: #555;
  cursor: pointer;
}

p:hover {
  text-decoration: underline;
}

.close-btn {
  position: absolute;
  top: 14px;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #333;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #007bff;
}

@media (max-width: 768px) {
  .modal-box {
    flex-direction: column;
  }

  .left-panel {
    display: none;
  }

  .right-panel {
    padding: 2rem;
  }
}
@media (max-width: 480px) {
  .modal-box {
    width: 95vw;
    margin: 0 1rem;
    border-radius: 8px;
  }

  .right-panel {
    padding: 1.5rem 1rem;
  }

  .right-panel h2 {
    font-size: 1.5rem;
    text-align: center;
  }

  form input[type="text"],
  form input[type="email"],
  form input[type="password"],
  form input[type="file"] {
    font-size: 0.95rem;
  }

  form button {
    font-size: 1rem;
    padding: 10px;
  }

  p {
    text-align: center;
    font-size: 0.9rem;
  }

  .close-btn {
    top: 12px;
    right: 12px;
    font-size: 1.3rem;
  }
}


</style>
