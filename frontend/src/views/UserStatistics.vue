<template>
  <div>
    <AdminNavbar />
    <div class="container mt-5">
      <!-- Heading -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="fw-semibold">
          <i class="fas fa-users me-2"></i> User Statistics |
          <span class="text-primary">Total: {{ filteredUsers.length }}</span>
        </h4>

        <!-- Search + CSV -->
        <div class="d-flex gap-2">
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Search by name or email..."
            class="form-control"
            style="width: 260px"
          />
          <button @click="exportToCSV" class="btn btn-outline-primary">
            <i class="fas fa-file-csv me-1"></i> Export CSV
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="table-responsive rounded shadow-sm border">
        <table class="table  table-hover align-middle text-center mb-0">
          <thead class="table-primary text-dark">
            <tr>
              <th>Actions</th>
              <th>#</th>
              <th>Profile</th>
              <th>Name</th>
              <th>Email</th>
              <th>Mobile</th>
              <th>Address</th>
              <th>Subscription</th>
              <th>Expiry</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in filteredUsers" :key="user.id"  @click="openUserModal(user)" class="cursor-pointer">
                       <td>
  <button class="btn btn-sm " @click.stop="confirmDelete(user)">
    <i class="fas fa-trash-alt"></i>
  </button>
</td>
              <td>{{ index + 1 }}</td>
              
              <td>
                <img
                  :src="getImageUrl(user.profile_image_url)"
                  alt="Profile"
                  class="rounded-circle border"
                  style="width: 45px; height: 45px; object-fit: cover; cursor:pointer"
                  @click="openUserModal(user)"
                />
              </td>
              <td>{{ user.name }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.mobile }}</td>
              <td>{{ user.address }}</td>
               <td>{{ user.post }}</td>
                <td>{{ user.description }}</td>
<td>
  <span v-if="user.is_subscribed" class="text-success fw-semibold">Active</span>
  <span v-else class="text-muted">Not Subscribed</span>
</td>
<td>
  <span v-if="user.is_subscribed && user.subscription_expiry">
    {{ formatDate(user.subscription_expiry) }}
  </span>
  <span v-else class="text-muted">—</span>
</td>         
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <!-- User Detail Modal -->
<div v-if="showUserModal" class="modal-backdrop-custom">
  <div class="modal-box p-4 text-center">
    <button class="btn-close position-absolute top-0 end-0 m-2" @click="showUserModal = false" />
    <img :src="getImageUrl(selectedUser.profile_image_url)" class="rounded-circle mb-3 shadow" style="width: 110px; height: 110px; object-fit: cover;" />
    <h5 class="fw-bold mb-1">{{ selectedUser.name }}</h5>
    <p class="mb-1 text-muted">{{ selectedUser.email }}</p>
    <p class="mb-1"><i class="fas fa-phone me-2"></i>{{ selectedUser.mobile }}</p>
    <p><i class="fas fa-map-marker-alt me-2"></i>{{ selectedUser.address }}</p>
    <hr class="my-3" />
    <div>
      <p class="mb-1">
        <strong>Subscription: </strong>
        <span
          :class="selectedUser.is_subscribed ? 'text-success fw-semibold' : 'text-danger fw-semibold'"
        >
          {{ selectedUser.is_subscribed ? 'Active' : 'Not Subscribed' }}
        </span>
      </p>
      <p v-if="selectedUser.is_subscribed && selectedUser.subscription_expiry">
        <strong>Expires on:</strong>
        {{ formatDate(selectedUser.subscription_expiry) }}
      </p>
    </div>
  </div>
</div>

<!-- Delete Confirmation Modal -->
<div v-if="showDeleteModal" class="delete-modal-backdrop">
  <div class="delete-modal-box">
    <h5 class="fw-semibold mb-3 text-danger">
      <i class="fas fa-exclamation-triangle me-2" />Confirm Delete
    </h5>
    <p class="text-muted">Are you sure you want to delete <strong>{{ userToDelete?.name }}</strong>?</p>
    <div class="d-flex justify-content-end gap-2 mt-4">
      <button class="btn btn-secondary btn-sm" @click="showDeleteModal = false">Cancel</button>
      <button class="btn btn-danger btn-sm" @click="deleteUser">Yes, Delete</button>
    </div>
  </div>
</div>


</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { toast } from 'vue3-toastify'
import AdminNavbar from '../components/AdminNavbar.vue'

const API = import.meta.env.VITE_API_URL
const users = ref([])
const searchTerm = ref('')
const showUserModal = ref(false)
const selectedUser = ref({})
const showDeleteModal = ref(false)
const userToDelete = ref(null)
const fetchUsers = async () => {
  try {
    const res = await axios.get(`${API}/users`)
    users.value = res.data
  } catch {
    toast.error('Failed to load users')
  }
}

const filteredUsers = computed(() =>
  users.value.filter(
    u =>
      u.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      u.email.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
)

const getImageUrl = (url) => {
  if (!url) return 'https://via.placeholder.com/45'
  return url.startsWith('http') ? url : `${API}${url}`
}

const exportToCSV = () => {
  const headers = ['Name', 'Email', 'Mobile', 'Address', 'Post/Position', 'Description', 'Subscription','Expiry']
  const rows = filteredUsers.value.map(u => [u.name, u.email, u.mobile, u.address, u.post, u.description ,u.is_subscribed ? 'Yes' : 'No',
  u.subscription_expiry ? formatDate(u.subscription_expiry) : ''])

  const csvContent = [
    headers.join(','),
    ...rows.map(r => r.join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'user_statistics.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
function showHover(url, e) {
  hoverImageUrl.value = getImageUrl(url)
  hoverX.value = e.clientX + 15
  hoverY.value = e.clientY + 15
}
function hideHover() {
  hoverImageUrl.value = null
}
function openUserModal(user) {
  selectedUser.value = user
  showUserModal.value = true
}
function confirmDelete(user) {
  userToDelete.value = user
  showDeleteModal.value = true
}

async function deleteUser() {
  const id = userToDelete.value.id 
  if (!id) return toast.error("Invalid user ID")

  try {
    await axios.delete(`${API}/users/${id}`)
    toast.success('User deleted successfully')
    showDeleteModal.value = false

    const loggedInUser = JSON.parse(localStorage.getItem('user'))
    console.log(loggedInUser)
    if (loggedInUser?.id === id) {
      localStorage.removeItem('user')
    } 

    fetchUsers()
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Failed to delete user')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

onMounted(fetchUsers)
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  position: relative;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
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

.image-preview-hover {
  position: fixed;
  z-index: 2000;
  pointer-events: none;
}
.image-preview-hover img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 10px;
  border: 2px solid #007bff;
}
@media (max-width: 768px) {
  /* Header: stack search + export button */
  .d-flex.justify-content-between.align-items-center.mb-4 {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .d-flex.gap-2 {
    flex-direction: column;
    gap: 0.5rem;
  }

  input.form-control {
    width: 100% !important;
  }

  .btn.btn-outline-primary {
    width: 100%;
  }

  /* Table: make each row scrollable */
  .table-responsive {
    overflow-x: auto;
  }

  /* Reduce padding for modal on smaller screens */
  .modal-box,
  .delete-modal-box {
    padding: 1.5rem;
    width: 90%;
    max-width: 95%;
  }

  .modal-box img {
    width: 90px;
    height: 90px;
  }

  .modal-box h5 {
    font-size: 1.2rem;
  }

  .modal-box p {
    font-size: 0.9rem;
  }

  .delete-modal-box h5 {
    font-size: 1rem;
  }

  .delete-modal-box p {
    font-size: 0.9rem;
  }

  .delete-modal-box .btn {
    font-size: 0.85rem;
  }

  .table th,
  .table td {
    font-size: 0.75rem;
    white-space: nowrap;
  }
}

</style>
