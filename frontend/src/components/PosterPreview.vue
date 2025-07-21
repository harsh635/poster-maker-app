<template>
  <div class="poster-wrapper">
   <div :class="['poster-box', template, { exporting: isExporting }]" :style="bgStyle">
      <!-- Logo (top-left corner) -->
      <div class="logo-container" v-if="data.showLogo">
        <template v-if="data.logoFileUrl">
          <img :src="data.logoFileUrl" class="logo-circle" />
        </template>
        <template v-else>
          <div class="logo-placeholder">Your Logo</div>
        </template>
        <button class="close-btn" @click="hide('showLogo')">×</button>
      </div>

      <!-- Employee Name (top-right corner for birthday only) -->
      <div
       v-if="normalizedOccasion === 'birthday' && data.showEmployeeName"
       class="employee-name"
       >
       🎂 {{ data.employeeName || 'Employee Name' }}
      <button class="close-btn" @click="hide('showEmployeeName')">×</button>
      </div>

      <!-- Main Content -->
      <div class="poster-content">
        <h1>{{ displayTitle }}</h1>
        <p>{{ displaySubtitle }}</p>
      </div>

      <!-- Bottom Info -->
      <div class="poster-bottom">
        <div class="bottom-left" v-if="data.showName">
          {{ data.name || 'Your Company Name' }}
            <button class="close-btn" @click="hide('showName')">×</button>
        </div>
        <div class="bottom-right" v-if="data.showPhone">
          📞 {{ data.phone || 'Phone Number' }}
              <button class="close-btn" @click="hide('showPhone')">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  template: String,
  data: Object,
  templateDetails: Object,
  isExporting: Boolean
})

const emit = defineEmits(['update:data'])

const normalizedOccasion = computed(() =>
  props.templateDetails?.occasion?.toLowerCase().trim() || ''
)



const displayTitle = computed(() => props.data?.title || props.templateDetails?.default_title || 'Your Poster Title')
const displaySubtitle = computed(() => props.data?.subtitle || props.templateDetails?.default_subtitle || 'Your Subtitle')

const bgStyle = computed(() => {
  const userBg = props.data?.imageFileUrl
  const defaultBg = props.templateDetails?.image
  const isExporting = props.data?.isExporting

   let imageUrl = userBg

   if (!userBg && defaultBg) {
    imageUrl = defaultBg.startsWith('http')
      ? defaultBg
      : `${import.meta.env.VITE_API_URL}${defaultBg}`
  }

  return {
    backgroundImage: `linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('${imageUrl}')`,
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  }
})

function hide(field) {
  emit('hideElement', field)
}

</script>


<style scoped>
.poster-wrapper {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.poster-box {
  position: relative;
  padding: 40px 20px;
  border-radius: 16px;
  background-size: cover;
  background-position: center;
  color: white;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  min-height: 345px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: 0.3s ease-in-out;
}

.poster-content h1 {
  font-size: 2.4rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.poster-content p {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

/* Logo Circle (Top Left) */
.logo-container {
  position: absolute;
  top: 15px;
  left: 20px;
  display: inline-block;
}

.logo-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.7);
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
  text-align: center;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.logo-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

/* Employee Name (Top Right) */
.employee-name {
  position: absolute;
  top: 20px;
  right: 20px;
  font-weight: 600;
  font-size: 1rem;
  background: rgba(0, 0, 0, 0.4);
  padding: 6px 12px;
  border-radius: 8px;
}

/* Bottom Information */
.poster-bottom {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
  font-weight: 500;
  opacity: 0.9;
}

.bottom-left,
.bottom-right {
  background: rgba(0, 0, 0, 0.4);
  padding: 6px 12px;
  border-radius: 8px;
  position:relative;
}
.close-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  color: #000;
  font-size: 14px;
  font-weight: bold;
  border-radius: 50%;
  cursor: pointer;
  width: 20px;
  height: 20px;
  line-height: 16px;
  padding: 0;
}
:deep(.exporting) .close-btn {
  display: none !important;
}
.poster-box.export-a4 h1 {
  font-size: 3rem;
}
.poster-box.export-instagram h1 {
  font-size: 2.4rem;
}
.poster-box.export-story h1 {
  font-size: 2.1rem;
}

.poster-box.export-a4 p {
  font-size: 1.6rem;
}
.poster-box.export-instagram p {
  font-size: 1.3rem;
}
.poster-box.export-story p {
  font-size: 1.2rem;
}

.poster-box.export-a4 .logo-circle,
.poster-box.export-a4 .logo-placeholder {
  width: 100px;
  height: 100px;
}

.poster-box.export-story .logo-circle,
.poster-box.export-story .logo-placeholder,
.poster-box.export-instagram .logo-circle,
.poster-box.export-instagram .logo-placeholder {
  width: 70px;
  height: 70px;
}
/* Example for Instagram (1080x1080) */
.export-instagram {
  width: 1080px;
  height: 1080px;
  font-size: 36px;
}

/* For A4 (2480x3508) */
.export-a4 {
  width: 2480px;
  height: 3508px;
  font-size: 64px;
}

/* Story (1080x1920) */
.export-story {
  width: 1080px;
  height: 1920px;
  font-size: 48px;
}

/* Force layout children to scale up too */
.export-instagram .poster-content h1,
.export-a4 .poster-content h1,
.export-story .poster-content h1 {
  font-size: 4em; /* You can tune this */
}

.export-instagram .logo-circle,
.export-a4 .logo-circle,
.export-story .logo-circle {
  width: 100px;
  height: 100px;
}


</style>
