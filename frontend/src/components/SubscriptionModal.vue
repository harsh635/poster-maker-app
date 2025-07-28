<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content text-center">
      <h4 class="mb-3">Buy Subscription Plan</h4>
      <p class="text-muted">Unlock Premium Features for 30 days</p>
      <button class="btn btn-primary mt-3 custom-green-btn" @click="subscribe" :disabled="isProcessingSubscription || isCheckingVip">{{ isProcessingSubscription ? 'Processing...' : 'Buy Subscription – ₹99' }}</button>
      <div class="vip-section mt-4">
        <input
          v-model="vipCode"
          placeholder="Enter VIP Code (if any)"
          class="form-control mb-2"
        />
        <button class="btn btn-success w-100 custom-green-btn" @click="applyVipCode" :disabled="isCheckingVip || isProcessingSubscription">
          {{ iisCheckingVip ? 'Checking...' : 'Apply VIP Code' }}
        </button>
      </div>
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
const vipCode = ref("")
const isProcessingSubscription = ref(false)
const isCheckingVip = ref(false)

function open() {
  visible.value = true
  vipCode.value = ""

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
      isProcessingSubscription.value = true
  try {
    await loadRazorpayScript()
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/create-order`, {
      amount: 9900 // ₹99.00
    })

    if (!res.data.order_id) {
    throw new Error('Invalid order data from server')
  }

    const options = {
      key: res.data.key_id,
      amount: res.data.amount,
      currency: res.data.currency,
      name: "Johar Jharkhand",
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

          const updatedUser = { ...props.user, is_subscribed: true, subscription_expiry: expiry,
            is_vip: false,
            vip_expiry: null }
          localStorage.setItem("user", JSON.stringify(updatedUser))
          emit("subscribed", updatedUser)
          toast.success("Subscription activated!")
          close()
        } catch (verifyError) {
          toast.error("Payment verification failed.")
          console.error(verifyError)
        } finally {
                    isProcessingSubscription.value = false

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
                 isProcessingSubscription.value = false

        toast.info("Payment cancelled")
    }
      }
    }

    const rzp = new window.Razorpay(options)
    rzp.open()
  } catch (err) {
    toast.error("Failed to start payment. Please try again.")
    console.error("Create Order Error:", err)
        isProcessingSubscription.value = false
  }
}
async function applyVipCode() {
  if (!vipCode.value.trim()) {
    toast.error("Please enter a VIP code.")
    return
  }

  isCheckingVip.value = true
  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/apply-vip-code`, {
      email: props.user.email,
      code: vipCode.value.trim()
    })

    if (res.data.success) {
      const updatedUser = { ...props.user, is_subscribed: true, is_vip: true,vip_expiry: res.data.vip_expiry || null,
        subscription_expiry: null  }
      localStorage.setItem("user", JSON.stringify(updatedUser))
      emit("subscribed", updatedUser)
      toast.success("VIP code applied! Subscription granted.")
      close()
    } else {
      toast.error(res.data.detail || "Invalid or expired code")
    }
  } catch (err) {
    toast.error(err.response?.data?.detail || "Failed to apply code")
  } finally {
        isCheckingVip.value = false

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
