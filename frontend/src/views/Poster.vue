<template>
 <div id="app">
 <main>
 <Navbar ref="navbarRef" />
  <div class="container py-5">
    <!-- FILTER -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-semibold">Select Poster Category</h4>
      <div class="position-relative">
      <i class="fas fa-filter filter-icon"></i>
      <select v-model="selectedOccasion" class="form-select filter-select">
        <option value="">All Categories</option>
        <option v-for="occasion in occasions" :key="occasion" :value="occasion">{{ occasion }}</option>
      </select>
    </div>
    </div>

    <!-- POSTER GRID -->
    <div class="row g-4 text-center">
      <div
        class="col-md-3"
        v-for="template in filteredTemplates"
        :key="template.id"
        @click="openModal(template.id)"
      >
        <div class="template-card p-3 rounded shadow-sm h-100 border">
          <img :src="getFullImageUrl(template.image)" alt="template" class="img-fluid rounded mb-2" style="height: 120px; object-fit: cover;" />
          <h6>{{ template.label }}</h6>
        </div>
      </div>
    </div>

    <!-- MODAL -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content single-wrapper">
        <!-- Close -->
       <button class="btn btn-close btn-lg close-absolute" @click="closeModal"></button>

          <!-- PREVIEW -->
           
      <FabricPoster
       ref="posterRef"
  :key="`${currentTemplate}-${formData.name}-${formData.post}`"
  :width="canvasWidth"
  :height="canvasHeight"
  :backgroundImage="formData.imageFileUrl || getFullImageUrl(currentTemplateDetails.image)"
  :profileImage="getImageUrl(user?.profile_image_url)"
  :name="formData.name"
  :post="formData.post"
  :description="formData.description"
  :phone="formData.phone"
  :title="formData.title"
  :subtitle="formData.subtitle"
/>

    <div class="modal-footer border-top bg-white p-3 d-flex flex-column flex-md-row justify-content-center gap-2">
  <button class="icon-button" @click="requireSubscription(() => posterRef?.exportAsPNG())" title="Download PNG">
    <i class="fas fa-download"></i>
    <span>Download</span>
  </button>

  <button class="icon-button" @click="posterRef?.sharePoster()" title="Share Poster">
    <i class="fas fa-share-alt"></i>
    <span>Share</span>
  </button>
</div>
      </div>
    </div>
  </div>
  </main>
<footer class="footer bg-light py-3 text-center text-muted small border-top">
     © 2025 Johar Jharkhand. All Right Reserved
    </footer>
  </div>


<!-- Full-Screen SVG Loader -->
<div v-if="loading" class="fullscreen-loader">
  <svg class="svg-spinner" viewBox="0 0 50 50">
    <circle
      class="path"
      cx="25"
      cy="25"
      r="20"
      fill="none"
      stroke-width="5"
    />
  </svg>
</div>
<SubscriptionModal ref="subscriptionModalRef" :user="user" @subscribed="onSubscribed" />


</template>

<script setup>
import { ref, computed , onMounted , nextTick} from 'vue'
import axios from 'axios'
import html2canvas from 'html2canvas'
import PosterPreview from '../components/PosterPreview.vue'
import { toast } from 'vue3-toastify'
import Navbar from '../components/Navbar.vue'
import SubscriptionModal from '../components/SubscriptionModal.vue'
import { useUser } from '../useUser'
import { onBeforeUnmount } from 'vue'
import FabricPoster from '../components/FabricPoster.vue'


const API_BASE = import.meta.env.VITE_API_URL
const isExporting = ref(false)

// Responsive canvas dimensions
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)
const canvasWidth = computed(() => {
  if (windowWidth.value < 768) {
    return Math.min(windowWidth.value - 60, 400)
  } else if (windowWidth.value < 1024) {
    return 450
  }
  return 500
})

const canvasHeight = computed(() => {
  if (windowWidth.value < 768) {
    return Math.min(windowWidth.value - 60, 400) // Square for mobile
  } else if (windowWidth.value < 1024) {
    return 450
  }
  return 500
})

function handleResize() {
  windowWidth.value = window.innerWidth
}

const navbarRef = ref()
const showModal = ref(false)
const selectedOccasion = ref('')
const posterRef = ref(null)
const templates = ref([])
const currentTemplate = ref('')
const currentTemplateDetails = ref({})
const loading = ref(false)
const { user, setUser } = useUser()
const subscriptionModalRef = ref()
const occasions = computed(() => [...new Set(templates.value.map(t => t.occasion))])
const filteredTemplates = computed(() =>
  !selectedOccasion.value
    ? templates.value
    : templates.value.filter(t => t.occasion === selectedOccasion.value)
)

const normalizedOccasion = computed(() =>
  currentTemplateDetails?.value?.occasion?.toLowerCase().trim() || ''
)

const selectedSize = ref('a4')

const exportSizes = {
  a4: { width: 2480, height: 3508, scale: 2 },
  instagram: { width: 1080, height: 1080, scale: 2 },
  story: { width: 1080, height: 1920, scale: 2 }
}

const formData = ref({
  title: '',
  subtitle: '',
  name: '',
  phone: '',
  post:'',
  description:'',
  employeeName: '',
  imageFileUrl: '',
  profileFileUrl:'',
  logoFileUrl: '',
  showLogo: true,
  showName: true,
  showPhone: true,
  showEmployeeName: true ,
  showProfile: true
})

const defaultTitleMap = ref({})
const defaultSubtitleMap = ref({})
const imageUrlMap = ref({})

const canExport = computed(() => {
  const hasBg = formData.value.imageFileUrl || currentTemplateDetails.value?.image
  return !!hasBg && !isExporting.value
})


function openModal(templateId) {
  const found = templates.value.find(t => t.id === templateId)
  currentTemplate.value = templateId
  currentTemplateDetails.value = found || {}
  showModal.value = true
  const rawImageUrl = imageUrlMap.value[templateId]
   
  document.body.style.overflow = 'hidden'

  formData.value = {
    title: defaultTitleMap.value[templateId] || '',
    subtitle: defaultSubtitleMap.value[templateId] || '',
    
    name: user.value?.name || '',
    phone: user.value?.mobile || '',
    post: user.value?.post || '',
    description: user.value?.description || '',
    profileFileUrl:user.value?.profile_image_url || '',
    employeeName: '',
    imageFileUrl: '',
    logoFileUrl: '',
    showLogo: true,
    showName: true,
    showPhone: true,
    showEmployeeName: true ,
     showProfile: true
  }
  console.log("📞 Loaded mobile number:", user.value?.mobile)
console.log("📝 Final formData:", JSON.parse(JSON.stringify(formData.value)))

    if (rawImageUrl?.startsWith('data:image')) {
    formData.value.imageFileUrl = rawImageUrl
  } else if (rawImageUrl) {
    convertImageUrlToBase64(rawImageUrl).then(base64 => {
      formData.value.imageFileUrl = base64
    })
  }
}

function requireSubscription(action) {
  if (!user.value.is_subscribed) {
    subscriptionModalRef.value?.open?.()
    return
  }
  action()
}

function onSubscribed(updatedUser) {
  setUser(updatedUser)
}

function onProfileUpload(event) {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = () => {
      formData.value.profileFileUrl = getFullImageUrl(user.value?.image || '')

    }
    reader.readAsDataURL(file)
  }
}


function convertImageUrlToBase64(url) {
  return fetch(url)
    .then(res => res.blob())
    .then(blob => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onloadend = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(blob)
      })
    })
    .catch(err => {
      console.error('Image to base64 failed:', err)
      return ''
    })
}


function closeModal() {
  showModal.value = false
  document.body.style.overflow = ''
}

function resetVisibility() {
  formData.value.title = ''
  formData.value.subtitle = ''
  formData.value.showLogo = true
  formData.value.showName = true
  formData.value.showPhone = true
  formData.value.imageFileUrl = ''
  formData.value.logoFileUrl = ''
  formData.value.showEmployeeName = true
}

function getFullImageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http') || path.startsWith('data:')) return path
  return `${API_BASE.replace(/\/$/, '')}/${path.replace(/^\//, '')}`
}

const getImageUrl = (url) => {
  if (!url) return ''
  return url.startsWith('http') ? url : `${API_BASE}${url}`
}


function onImageUpload(event) {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = () => {
      formData.value.imageFileUrl = reader.result
    }
    reader.readAsDataURL(file)
  }
}

function onLogoUpload(event) {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = () => {
      formData.value.logoFileUrl = reader.result
    }
    reader.readAsDataURL(file)
  }
}

async function toBase64(url) {
  try {
    const response = await fetch(url, { mode: 'cors' });

    if (!response.ok) {
      throw new Error(`Failed to fetch ${url} – status ${response.status}`);
    }

    const blob = await response.blob();

    return await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    console.error("❌ Base64 conversion failed:", error.message);
    return null;
  }
}

async function exportAsImage() {
  isExporting.value = true
  await nextTick()

  const el = document.querySelector(".poster-box")
  if (!el) {
    console.error("Poster element not found")
    isExporting.value = false
    return
  }

  // Step 1: Convert background image to base64
  let bgUrl = formData.value.imageFileUrl || currentTemplateDetails.value?.image
  if (bgUrl && !bgUrl.startsWith('http') && !bgUrl.startsWith('data')) {
    bgUrl = `${import.meta.env.VITE_API_URL}${bgUrl}`
  }
  const base64Bg = await toBase64(bgUrl)
  if (!base64Bg) {
    console.error("Failed to convert background to base64")
    isExporting.value = false
    return
  }

  // Step 2: Clone the poster element
  const clone = el.cloneNode(true)
  const sizeClass = `export-${selectedSize.value}`

  // Add export class to cloned element
  clone.classList.add(sizeClass)
  clone.style.position = 'fixed'
  clone.style.top = '-9999px'
  clone.style.left = '-9999px'
  clone.style.zIndex = '-1'

  // Replace background image
  clone.style.backgroundImage = `linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('${base64Bg}')`

  // Append clone to body
  document.body.appendChild(clone)

  // Step 3: Export from cloned node
  try {
    clone.querySelectorAll('.close-btn').forEach(btn => btn.remove())
    const canvas = await html2canvas(clone, {
      useCORS: true,
      backgroundColor: null
    })

    const link = document.createElement('a')
    link.download = `${currentTemplate.value}_poster.png`
    link.href = canvas.toDataURL()
    link.click()
  } catch (err) {
    console.error("html2canvas failed:", err)
  } finally {
    document.body.removeChild(clone) // Clean up
    isExporting.value = false
  }
}


async function fetchTemplates() {
  try {
    const res = await axios.get(`${API_BASE}/templates`)
    templates.value = res.data

    res.data.forEach(t => {
      defaultTitleMap.value[t.id] = t.default_title
      defaultSubtitleMap.value[t.id] = t.default_subtitle
      imageUrlMap.value[t.id] = getFullImageUrl(t.image_url)
    })
  } catch (err) {
    console.error('Failed to fetch templates:', err)
  }
}

async function savePosterData() {
  loading.value = true
  const title = formData.value.title || defaultTitleMap.value[currentTemplate.value]
  const subtitle = formData.value.subtitle || defaultSubtitleMap.value[currentTemplate.value]


  const payload = {
    title,
    subtitle,
    phone: formData.value.phone,
    company: formData.value.name,
    employee_name: formData.value.employeeName,
    template_name: currentTemplate.value,
    logo_url: formData.value.logoFileUrl || ''
  }

  try {
    const res = await axios.post(`${API_BASE}/save_poster/`, payload)
     toast.success("Poster saved successfully.")
  } catch (err) {
    console.error(err)
    toast.error("Failed to save poster.")
  } finally {
    loading.value = false
  }
}


onMounted(() => {
  if (!user.value) {
    navbarRef.value.openAuthModal('login')
    return router.push('/')
  }

  window.addEventListener('resize', handleResize)
  fetchTemplates()
})


onBeforeUnmount(() => {
  document.body.style.overflow = ''
  window.removeEventListener('resize', handleResize)
})

</script>

<style scoped>
.template-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.template-card:hover {
  transform: scale(1.02);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.08);
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 10, 0.4);
  backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  overflow: auto;
  padding: 1rem;
}

/* Modal Box */
.modal-content {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  width: auto;
  max-width: 95vw;
  max-height: 95vh;
  position: relative;
  box-shadow: none;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  overflow: visible;
}


/* Close button outside the top-right of the white box */
.close-absolute {
  color: black;
  position: absolute;
  top: -10px;
  right: -10px;
  z-index: 1100;
  padding: 0.4rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

  main {
    flex: 1;
  }
  html, body {
    height: 100%;
    margin: 0;
  }
#app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  .fullscreen-loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(6px);
  z-index: 3000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.svg-spinner {
  animation: rotate 2s linear infinite;
  width: 60px;
  height: 60px;
}

.svg-spinner .path {
  stroke: #007bff; /* Bootstrap primary */
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}
.filter-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  pointer-events: none;
  font-size: 0.9rem;
}

.filter-select {
  padding-left: 2rem;
  height: 38px;
  border: 1.5px solid #ced4da;
  border-radius: 5px;
}

.poster-box.exporting .close-btn {
  display: none !important;
}
.footer {
  background-color: #e9f3eb;
  color: #555;
  font-weight: 500;
  padding: 1rem;
  border-top: 1px solid #cce5d2;
}
.icon-button {
  background: #0E5D39;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.icon-button i {
  font-size: 16px;
}

.icon-button:hover {
  background:  #0c4f30;
}
/* Responsive adjustments */
@media (max-width: 768px) {
  .container.py-5 {
    padding: 1rem;
  }

  .d-flex.justify-content-between.align-items-center.mb-4 {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .filter-select {
    width: 100%;
    margin-top: 0.5rem;
  }

  .row > [class^="col-"] {
    flex: 0 0 100%;
    max-width: 100%;
  }

  .template-card {
    margin-bottom: 1rem;
  }

  .modal-overlay {
    padding: 10px;
  }

  .modal-content {
    max-width: 100%;
    max-height: 100%;
  }

  .poster-wrapper {
    padding: 1rem;
    max-width: 100%;
    max-height: 100%;
  }

  .close-absolute {
    top: -5px;
    right: -5px;
    padding: 0.3rem;
  }

  footer {
    font-size: 0.8rem;
    padding: 1rem 0;
  }
  
  .modal-footer {
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }
  .modal-content{
    padding:  0.75rem;
  }
   .icon-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 5px;
  }
  
  .poster-wrapper {
    padding: 0.5rem;
    border-radius: 8px;
  }
  
  .close-absolute {
    top: 0;
    right: 0;
    padding: 0.2rem;
  }
  .modal-content{
    padding: 0.5 rem;
    border-radius: 10px;
  }
}
</style>