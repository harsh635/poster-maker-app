<template>
  <div class="modal-overlay" v-if="visible">
    <div class="modal-content">
      <h5 class="mb-3">Generate VIP Access Code</h5>
      <input v-model="email" type="email" class="form-control mb-3" placeholder="Enter user email" />

      <button class="btn btn-primary w-100 custom-green-btn" @click="generate" :disabled="loading">
        {{ loading ? 'Generating...' : 'Generate Code' }}
      </button>

      <div v-if="code" class="alert alert-success mt-3">
        <strong>Code:</strong> {{ code }}<br />
        <small>Valid until: {{ expiryDate }}</small>
      </div>

      <button class="btn btn-outline-secondary mt-3 w-100" @click="close">Close</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { toast } from 'vue3-toastify'

const visible = ref(false)
const email = ref('')
const code = ref('')
const expiryDate = ref('')
const loading = ref(false)

function open() {
  visible.value = true
  email.value = ''
  code.value = ''
  expiryDate.value = ''
}
function close() {
  visible.value = false
}

async function generate() {
  if (!email.value.trim()) return toast.error("Enter a valid email")

  loading.value = true
  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/admin/generate-vip-code`, {
      admin_email: "admin@example.com", // Replace with dynamic admin if needed
      email: email.value,
    })
    code.value = res.data.code
    expiryDate.value = new Date(res.data.expiry).toLocaleDateString('en-IN')
    toast.success("Code generated!")
  } catch (err) {
    toast.error(err.response?.data?.detail || "Failed to generate code")
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}
.modal-content {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
}

.custom-green-btn {
  background-color: #0E5D39 !important;
  border-color: #0E5D39 !important;
  color: #fff !important;
}

.custom-green-btn:hover,
.custom-green-btn:focus {
  background-color: #0c4f30 !important;
  border-color: #0c4f30 !important;
}
</style>
