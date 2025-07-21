<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content text-center">
      <h4 class="mb-3">Buy Subscription Plan</h4>
      <p class="text-muted">Unlock Premium Features for 30 days</p>
      <button class="btn btn-primary mt-3" @click="subscribe" :disabled="isLoading">{{ isLoading ? 'Processing...' : 'Buy Subscription – ₹199' }}</button>
      <button class="btn btn-outline-secondary mt-2" @click="close">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { toast } from 'vue3-toastify'

const props = defineProps(['user'])
const emit = defineEmits(['subscribed'])

const visible = ref(false)
const isLoading = ref(false)

function open() {
  visible.value = true
}
function close() {
  visible.value = false
}

// Dynamically load Razorpay script if not present
async function loadRazorpayScript() {
  if (typeof window.Razorpay !== 'undefined') return

  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load Razorpay SDK'))
    document.head.appendChild(script)
  })
}

async function subscribe() {
    isLoading.value = true
  try {
    await loadRazorpayScript()
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/create-order`, {
      amount: 19900 // ₹199.00
    })

    if (!res.data.order_id) {
    throw new Error('Invalid order data from server')
  }

    const options = {
      key: res.data.key_id,
      amount: res.data.amount,
      currency: res.data.currency,
      name: "Poster Maker Pro",
      description: "1 Month Premium Access",
      order_id: res.data.order_id,
      handler: async function (response) {
        try {
          // ✅ Send all values from Razorpay to backend
          const verifyRes = await axios.post(`${import.meta.env.VITE_API_URL}/verify-payment`, {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
            email: props.user.email
          })

          const updatedUser = { ...props.user, is_subscribed: true }
          localStorage.setItem("user", JSON.stringify(updatedUser))
          emit("subscribed", updatedUser)
          toast.success("Subscription activated!")
          close()
        } catch (verifyError) {
          toast.error("Payment verification failed.")
          console.error(verifyError)
        } finally {
          isLoading.value = false
        }
      },
      prefill: {
        name: props.user.name,
        email: props.user.email,
      },
      theme: {
        color: "#007bff",
      },
      modal: {
        ondismiss: function () {
        isLoading.value = false
        toast.info("Payment cancelled")
    }
      }
    }

    const rzp = new window.Razorpay(options)
    rzp.open()
  } catch (err) {
    toast.error("Failed to start payment. Please try again.")
    console.error("Create Order Error:", err)
  }
}
defineExpose({ open })
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.modal-content {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
}
</style>
