<template>
  <div class="landing-page">
   <Navbar ref="navbarRef" />
    <section class="hero-section d-flex align-items-center justify-content-between px-5 py-5 bg-white">
      <div class="text-start">
        <h1 class="display-3 fw-bold">Design Your Own Posters</h1>
        <p class="lead mt-3">Create custom posters for festivals, birthdays, and more in seconds.</p>
        <button class="btn btn-outline-primary btn-lg mt-4" @click="handleAllPosters">
         {{ user?.is_subscribed ? '🎨 Start Designing' : '💎 Buy Premium' }}
        </button>
      </div>
      <div>
      <img src="/templates/banner.png" alt="hero poster" style="max-width: 500px" />
      </div>
    </section>

        <SubscriptionModal ref="subscriptionModalRef" :user="user" @subscribed="onSubscribed" />

     <footer class="bg-light py-4 text-center text-muted small border-top">
    © 2025 TechGo, Inc. All rights reserved.
  </footer>

  <!-- Floating Ad Banner -->
   <!-- <div v-if="showAd" class="large-floating-ad">
      <img src="/templates/addbanner.png" alt="Ad" />
      <button class="close-btn" @click="showAd = false">×</button>
    </div> -->


  </div>
</template>
<script setup>
import { ref, onMounted , watch} from 'vue'
import { useRouter } from 'vue-router'
import AuthModal from '../components/AuthModal.vue'
import Navbar from '../components/Navbar.vue'
import SubscriptionModal from '../components/SubscriptionModal.vue'
import  {useUser} from '../useUser'

const router = useRouter()
const navbarRef = ref()
const subscriptionModalRef = ref()
const { user, setUser } = useUser()
const showAd = ref(true)

function handleAllPosters() {
  if (!user.value) {
    navbarRef.value.openAuthModal('login')
  } else if (!user.value.is_subscribed) {
    subscriptionModalRef.value?.open?.()
  } else {
    router.push('/posters')
  }
}


function onSubscribed(updatedUser) {
  setUser(updatedUser)
  router.push('/posters')
}

onMounted(() => {
  // Optional: persist dismissal in session
  if (sessionStorage.getItem('adDismissed') === 'true') {
    showAd.value = false
  }
})

watch(showAd, (val) => {
  if (!val) sessionStorage.setItem('adDismissed', 'true')
})

</script>

<style scoped>
.hero-section {
  flex-wrap: wrap;
  gap: 2rem;
}

.hero-section h1 {
  font-size: 2.5rem;
}

.hero-section img {
  max-width: 100%;
  height: auto;
}

/* Mobile styles */
@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
    padding: 2rem 1rem;
  }

  .hero-section h1 {
    font-size: 2rem;
  }

  .hero-section p {
    font-size: 1.1rem;
  }

  .hero-section button {
    width: 100%;
  }
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
  right: 10px;
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

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.large-floating-ad {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 40vw;
  height: 50vh;
  background: white;
  border-top-left-radius: 12px;
  box-shadow: -4px -4px 20px rgba(0, 0, 0, 0.2);
  z-index: 2000;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.large-floating-ad img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.large-floating-ad .close-btn {
  position: absolute;
  top: 10px;
  right: 12px;
  background: rgba(255, 255, 255, 0.85);
  border: none;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 50%;
  z-index: 100;
}
</style>
