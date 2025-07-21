<template>
 <div id="app">
 <main>
 <Navbar ref="navbarRef" />
  <div class="container py-5">
    <!-- FILTER -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-semibold">All Poster Templates</h4>
      <div class="position-relative">
      <i class="fas fa-filter filter-icon"></i>
      <select v-model="selectedOccasion" class="form-select filter-select">
        <option value="">All Occasions</option>
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
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <!-- Close -->
        <button class="btn btn-close btn-sm position-absolute top-0 end-0 m-3" @click="closeModal"></button>

        <!-- Form & Preview -->
        <div class="row">
          <!-- FORM -->
          <div class="col-md-6">
            <h5 class="fw-semibold mb-3">Edit Poster:</h5>
            <input type="text" class="form-control mb-2" placeholder="Title" v-model="formData.title" />
            <input type="text" class="form-control mb-2" placeholder="Subtitle" v-model="formData.subtitle" />
            <input type="text" class="form-control mb-2" placeholder="Company Name" v-model="formData.name" />
            <input type="text" class="form-control mb-2" placeholder="Phone Number" v-model="formData.phone" />

           <input v-if="normalizedOccasion === 'birthday'" type="text"
            class="form-control mb-2"
            placeholder="Employee Name"
            v-model="formData.employeeName" />

            <label class="form-label">Upload Image</label>
            <input type="file" class="form-control mb-2" @change="onImageUpload" />
            <label class="form-label">Upload Logo</label>
            <input type="file" class="form-control mb-2" @change="onLogoUpload" />
            <label class="form-label">Select Poster Size</label>
            <select v-model="selectedSize" class="form-select mb-2">
             <option value="a4">A4 (2480x3508)</option>
             <option value="instagram">Instagram (1080x1080)</option>
             <option value="story">Story (1080x1920)</option>
            </select>
            <button class="btn btn-success me-2 mt-2" @click="exportAsImage" :disabled="!canExport">
            <span v-if="isExporting">Exporting...</span>
            <span v-else>Export as PNG</span>
            </button>
            <button class="btn btn-outline-primary mt-2 me-2" @click="savePosterData()">
             Save Poster
            </button>
            <button class="btn btn-warning mt-2 " @click="resetVisibility">Reset Fields</button>

          </div>
          


          <!-- PREVIEW -->
          <div class="col-md-6">
            <h5 class="fw-semibold mb-3">Live Preview:</h5>
            <div ref="posterRef" :class="{ exporting: isExporting }">
              <PosterPreview
              :template="currentTemplate"
              :templateDetails="currentTemplateDetails"
              :data="formData"
              :isExporting="isExporting"
               @hideElement="field => formData[field] = false"
              :key="currentTemplate + JSON.stringify(formData)" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </main>
     <footer class="bg-light py-4 text-center text-muted small border-top">
    © 2025 TechGo, Inc. All rights reserved.
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


const API_BASE = import.meta.env.VITE_API_URL
const isExporting = ref(false)

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
  employeeName: '',
  imageFileUrl: '',
  logoFileUrl: '',
  showLogo: true,
  showName: true,
  showPhone: true,
  showEmployeeName: true 
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

  formData.value = {
    title: defaultTitleMap.value[templateId] || '',
    subtitle: defaultSubtitleMap.value[templateId] || '',
    name: '',
    phone: '',
    employeeName: '',
    imageFileUrl: '',
    logoFileUrl: '',
    showLogo: true,
    showName: true,
    showPhone: true,
    showEmployeeName: true 
  }
    if (rawImageUrl?.startsWith('data:image')) {
    formData.value.imageFileUrl = rawImageUrl
  } else if (rawImageUrl) {
    convertImageUrlToBase64(rawImageUrl).then(base64 => {
      formData.value.imageFileUrl = base64
    })
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

  if (!user.value.is_subscribed) {
    subscriptionModalRef.value?.open?.()
    return router.push('/')
  }

  fetchTemplates()
})


function onSubscribed(updatedUser) {
  setUser(updatedUser)
}


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
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(10, 10, 10, 0.4);
  backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* Modal Box */
.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 1000px;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
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

  .modal-content {
    padding: 1rem;
    overflow-y: auto;
    max-height: 95vh;
  }

  .modal-content .row {
    flex-direction: column;
  }

  .modal-content .col-md-6 {
    width: 100%;
    margin-bottom: 1rem;
  }

  footer {
    font-size: 0.8rem;
    padding: 1rem 0;
  }
}

</style>
