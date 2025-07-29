<template>
  <div>
    <AdminNavbar @open-generate-modal="openGenerateModal" />
    <GenerateVipCodeModal ref="vipModalRef" />
    <div class="container py-5">
      <!-- Header -->
      <div
        class="d-flex justify-content-between align-items-center mb-4 flex-wrap"
      >
        <h4 class="fw-semibold mb-2 mb-md-0">Template Library</h4>
        <div class="d-flex align-items-center gap-2">
          <!-- Add New Template Button -->
          <button
            class="btn btn-outline-primary d-flex align-items-center gap-2"
            @click="openModal('create')"
          >
            <i class="fas fa-plus"></i>
            <span>Add Template</span>
          </button>

          <!-- KPI Buttons -->
          <div class="kpi-buttons d-flex gap-2 flex-wrap">
            <button
              v-for="kpi in [
                'Good Morning',
                'Recent Updates',
                'Upcoming Events',
              ]"
              :key="kpi"
              class="btn"
              :class="{
                'btn-outline-primary': kpi === 'Good Morning',
                'btn-outline-success': kpi === 'Recent Updates',
                'btn-outline-warning': kpi === 'Upcoming Events',
                active: selectedKPI === kpi,
              }"
              @click="selectKPI(kpi)"
            >
              {{ kpi }}
            </button>
          </div>
        </div>
      </div>
      <!-- LOADING MESSAGE -->
<div v-if="loading" class="text-center my-5">
  <div class="spinner-border text-primary mb-3" role="status">
    <span class="visually-hidden">Loading...</span>
  </div>
  <p class="text-muted">Loading templates, please wait...</p>
</div>

      <!-- Poster Grid -->
      <div v-else class="row g-4 text-center">
        <div v-for="t in filteredTemplates" :key="t.id" class="col-md-3">
          <div
            class="template-card p-3 rounded shadow-sm h-100 border position-relative"
            @click="openModal('edit', t)"
          >
            <!-- Delete button (stop click from bubbling) -->
            <button
              class="btn btn-sm btn-danger position-absolute top-0 end-0 m-2"
              @click.stop="confirmDelete(t.id)"
            >
              <i class="fas fa-times"></i>
            </button>

            <img
              :src="getFullImageUrl(t.image)"
              class="img-fluid rounded mb-2"
              style="height: 120px; object-fit: cover"
            />
            <h6>{{ t.label }}</h6>
          </div>
        </div>
      </div>

      <!-- Modal -->
      <div v-if="showModal" class="modal-overlay">
        <div class="modal-content">
          <button
            class="btn-close position-absolute top-0 end-0 m-3"
            @click="closeModal"
          />
          <div class="row">
            <!-- Form -->
            <div class="col-md-6">
              <h5 class="fw-semibold mb-3">
                {{ modalMode === "create" ? "Add" : "Edit" }} Template
              </h5>
              <input
                v-model="form.label"
                class="form-control mb-2"
                placeholder="Label"
              />

              <!-- Good Morning has no title/subtitle/date -->
              <div v-if="selectedKPI !== 'Good Morning'">
                <input
                  v-model="form.default_title"
                  class="form-control mb-2"
                  placeholder="Your Poster Title"
                />
                <input
                  v-model="form.default_subtitle"
                  class="form-control mb-2"
                  placeholder="Your Subtitle"
                />
                <input
                  v-model="form.date"
                  type="date"
                  class="form-control mb-2"
                  placeholder="Date"
                />
              </div>

              <label class="form-label mt-2">Upload Background Image</label>
              <input
                type="file"
                class="form-control mb-3"
                @change="onImageUpload"
              />
              <button class="btn btn-primary" @click="submitTemplate">
                {{ modalMode === "create" ? "Create" : "Update" }} Template
              </button>
            </div>

            <!-- Preview -->
            <div class="col-md-6">
              <h5 class="fw-semibold mb-3">Live Preview</h5>
              <PosterPreview
                :template="form.label"
                :templateDetails="modalTemplateDetails"
                :data="previewData"
                :key="form.label + JSON.stringify(previewData)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Delete Confirmation Modal -->
  <div v-if="showDeleteConfirm" class="delete-modal-backdrop">
    <div class="delete-modal-box">
      <h5 class="fw-semibold mb-3">
        <i class="fas fa-exclamation-triangle me-2" />Confirm Delete
      </h5>
      <p class="text-muted">Are you sure you want to delete this template?</p>
      <div class="d-flex justify-content-end gap-2 mt-4">
        <button class="btn btn-secondary btn-sm" @click="cancelDelete">
          Cancel
        </button>
        <button
          class="btn btn-danger btn-sm"
          @click="deleteTemplate(confirmDeleteId)"
        >
          Yes, Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { toast } from "vue3-toastify";
import AdminNavbar from "../components/AdminNavbar.vue";
import PosterPreview from "../components/PosterPreview.vue";
import GenerateVipCodeModal from "../components/GenerateVipCodeModal.vue";
const API = import.meta.env.VITE_API_URL;

// State
const templates = ref([]);
const selectedKPI = ref("Good Morning"); // default selection
const showModal = ref(false);
const modalMode = ref("create");
const imageFile = ref(null);
const currentTemplateId = ref(null);
const showDeleteConfirm = ref(false);
const confirmDeleteId = ref(null);
const vipModalRef = ref(null)
const loading = ref(false)
const form = ref({
  label: "",
  occasion: selectedKPI.value,
  default_title: "",
  default_subtitle: "",
  date: "",
});

// Computed
const occasions = computed(() => [
  ...new Set(templates.value.map((t) => t.occasion)),
]);
const filteredTemplates = computed(() =>
  templates.value.filter((t) => t.occasion === selectedKPI.value)
);

const previewData = computed(() => {
  const isGoodMorning = selectedKPI.value === 'Good Morning'
  return {
    title: isGoodMorning ? '' : form.value.default_title,
    subtitle: isGoodMorning ? '' : form.value.default_subtitle,
    date: isGoodMorning ? '' : form.value.date,
    name: '',
    phone: '',
    employeeName: '',
    imageFileUrl: imageFile.value ? URL.createObjectURL(imageFile.value) : ''
  }
})


const modalTemplateDetails = computed(() => {
  const fallback = templates.value.find(
    (t) => t.id === currentTemplateId.value
  );
  return {
    ...form.value,
    image: imageFile.value
      ? URL.createObjectURL(imageFile.value)
      : fallback?.image || "",
  };
});

import { nextTick } from 'vue'

function openGenerateModal() {
  nextTick(() => {
    if (vipModalRef.value?.open) {
      vipModalRef.value.open()
    } else {
      toast.error("Modal not available yet.")
    }
  })
}

// Methods
function getFullImageUrl(path) {
  if (!path) return "";
  return path.startsWith("http") ? path : `${API}${path}`;
}

async function fetchTemplates() {
  loading.value = true
  try {
    const res = await axios.get(`${API}/templates`);
    templates.value = res.data;
  } catch (err) {
    toast.error("Failed to load templates.");
  }finally{
    loading.value = false
  }
}

function openModal(mode, template = null) {
  document.body.style.overflow = "hidden";
  modalMode.value = mode;
  if (mode === "edit" && template) {
    form.value = {
      label: template.label,
      occasion: template.occasion,
      default_title: template.default_title,
      default_subtitle: template.default_subtitle,
    };
    currentTemplateId.value = template.id;
  } else {
    form.value = {
      label: "",
      occasion: selectedKPI.value,
      default_title: "",
      default_subtitle: "",
      date: "",
    };
    currentTemplateId.value = null;
  }
  imageFile.value = null;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  document.body.style.overflow = "";
}

function onImageUpload(e) {
  imageFile.value = e.target.files[0];
}

async function submitTemplate() {
  const formData = new FormData();
  formData.append("label", form.value.label);
  formData.append("occasion", form.value.occasion);
  formData.append("default_title", form.value.default_title);
  formData.append("default_subtitle", form.value.default_subtitle);
  formData.append("date", form.value.date);

  if (imageFile.value) formData.append("image", imageFile.value);

  try {
    if (modalMode.value === "create") {
      await axios.post(`${API}/templates/upload`, formData);
      toast.success("Template created successfully.");
    } else {
      await axios.put(`${API}/templates/${currentTemplateId.value}`, formData);
      toast.success("Template updated successfully.");
    }
    await fetchTemplates();
    closeModal();
  } catch (err) {
    toast.error(err.response?.data?.detail || "Operation failed.");
  }
}

function confirmDelete(id) {
  confirmDeleteId.value = id;
  showDeleteConfirm.value = true;
}

function cancelDelete() {
  confirmDeleteId.value = null;
  showDeleteConfirm.value = false;
}
function selectKPI(kpi) {
  selectedKPI.value = kpi;
}

async function deleteTemplate(id) {
  try {
    await axios.delete(`${API}/templates/${id}`);
    toast.success("Template deleted successfully.");
    await fetchTemplates();
  } catch {
    toast.error("Failed to delete template.");
  } finally {
    showDeleteConfirm.value = false;
    confirmDeleteId.value = null;
  }
}

onMounted(fetchTemplates);
</script>

<style scoped>
.template-card {
  cursor: pointer;
  transition: transform 0.2s ease;
  position: relative;
}
.template-card:hover {
  transform: scale(1.03);
}
.delete-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.15); /* subtle dim */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.delete-modal-box {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.2s ease-out;
  text-align: left;
}

@keyframes slideIn {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 10, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  backdrop-filter: blur(4px);
  padding: 1rem; /* ⬅️ Ensures modal has breathing room on small screens */
  box-sizing: border-box;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 1000px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
  position: relative;
}

.btn-outline-primary {
  border-width: 1px;
  font-weight: 500;
}
.btn-outline-primary:hover {
  background-color: #0d6efd;
  color: white;
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
.btn.active {
  color: white !important;
}
.btn-outline-primary.active {
  background-color: #0d6efd;
}
.btn-outline-success.active {
  background-color: #198754;
}
.btn-outline-warning.active {
  background-color: #ffc107;
}

@media (max-width: 768px) {
  /* Stack header actions vertically */
  .d-flex.justify-content-between.align-items-center.mb-4.flex-wrap {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .d-flex.align-items-center.gap-2 {
    flex-wrap: wrap;
    justify-content: space-between;
  }

  .filter-select {
    width: 100%;
  }

  /* Poster grid - 1 per row on mobile */
  .row > .col-md-3 {
    flex: 0 0 100%;
    max-width: 100%;
  }

  .template-card {
    margin-bottom: 1rem;
  }

  /* Modal: Stack content vertically */
  .modal-content .row {
    flex-direction: column;
  }

  .modal-content .col-md-6 {
    width: 100%;
    margin-bottom: 1rem;
  }

  /* Delete modal spacing */
  .delete-modal-box {
    margin: 0 1rem;
    padding: 1.5rem;
  }

  /* Reduce modal padding for small screens */
  .modal-content {
    padding: 1.2rem;
    max-height: 90vh;
    overflow-y: auto;
    border-radius: 10px;
  }
}
.kpi-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .kpi-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .kpi-buttons .btn {
    width: 100%;
  }
}

</style>
