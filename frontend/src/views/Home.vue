<template>
  <div class="landing-page">
    <Navbar ref="navbarRef" />

    <main class="hero-section">
      <div class="content-container">
        <div class="text-block">
          <h1 class="fw-bold">Design Your Own Jharkhand Mukti Morcha Posters</h1>
          <p class="lead mt-3">A Poster Maker Dedicated to JMM- Create, Customise and share your Voice with the Party's Colors!</p>
          <button class="btn btn-outline-primary btn-lg mt-4" @click="handleAllPosters">
            {{ '🎨 Start Designing' }}
          </button>
        </div>
        <div class="image-block">
          <img src="/templates/Banner Johar.png" alt="hero poster" />
        </div>
      </div>
    </main>


    <footer class="footer bg-light py-3 text-center text-muted small border-top">
      © 2025 Johar Jharkhand. All Right Reserved
    </footer>
  </div>
</template>


<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import { useUser } from '../useUser'

const router = useRouter()
const navbarRef = ref()
const { user, setUser } = useUser()
const showAd = ref(true)

function handleAllPosters() {
  if (!user.value) {
    navbarRef.value.openAuthModal('login')
  }  else {
    router.push('/posters')
  }
}


onMounted(() => {
  if (sessionStorage.getItem('adDismissed') === 'true') {
    showAd.value = false
  }
})

watch(showAd, (val) => {
  if (!val) sessionStorage.setItem('adDismissed', 'true')
})
</script>

<style scoped>
.landing-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f2f9f5; /* Soft light green for contrast */
}

.hero-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background-color: #f2f9f5;
}

.content-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  max-width: 1200px;
  width: 100%;
}

.image-block img {
  max-width: 450px;
  width: 100%;
  height: auto;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-radius: 1rem;
}

.image-block img:hover {
  box-shadow: 0 12px 30px rgba(14, 93, 57, 0.4);
  transition: box-shadow 0.3s ease;
}

.text-block {
  flex: 1;
  padding-right: 1rem;
}

.text-block h1 {
  font-size: 2.8rem;
  margin-bottom: 1rem;
  color: #0E5D39;
}

.text-block p {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: #333;
}

.text-block button {
  font-size: 1.1rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  background-color: #0E5D39;
  color: white;
  border: none;
  transition: background-color 0.3s ease;
}
.text-block button:hover {
  background-color: #0c4f30;
}

/* Footer */
.footer {
  background-color: #e9f3eb;
  color: #555;
  font-weight: 500;
  padding: 1rem;
  border-top: 1px solid #cce5d2;
}

/* Mobile */
@media (max-width: 768px) {
  .content-container {
    flex-direction: column;
    text-align: center;
  }

  .text-block {
    padding: 0;
  }

  .text-block h1 {
    font-size: 2rem;
  }

  .text-block p {
    font-size: 1rem;
  }

  .text-block button {
    width: 100%;
    font-size: 1rem;
  }

  .image-block img {
    max-width: 300px;
    margin-top: 2rem;
  }
}



</style>
