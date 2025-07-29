<template>
  <div class="canvas-wrapper">
    <canvas
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      class="poster-canvas"
    />

     <!-- <input
    type="file"
    accept="image/*"
    ref="fileInputRef"
    class="hidden-input"
    @change="handleProfileChange"
  /> -->

  <!-- Context menu for profile image -->
    <!-- <div
      v-if="showProfileMenu"
      ref="profileMenuRef"
      class="profile-context-menu"
      :style="{ left: `${menuX}px`, top: `${menuY}px` }"
    >
      <button @click="triggerProfileUpload">📁 Change Profile Image</button>
    </div> -->

    <div
  v-if="showToolbar && selectedText"
  class="floating-toolbar"
  :style="{ left: `${toolbarX}px`, top: `${toolbarY}px` }"
  @mousedown.stop
>
  <div
  class="toolbar-row drag-handle"
  @mousedown.stop.prevent="startDrag"
  @touchstart.stop.prevent="startDrag"
>

    <label>
      Size
      <input type="number" v-model="fontSize" @input="debouncedUpdateFontSize" />
    </label>

    <label>
      Color
      <input type="color" v-model="fontColor" @input="updateFontColor" />
    </label>

    <label>
    Font:
    <select v-model="fontFamily" @change="updateFontFamily">
      <option value="Arial">Arial</option>
      <option value="Poppins">Poppins</option>
      <option value="Times New Roman">Times New Roman</option>
      <option value="Roboto">Roboto</option>
      <option value="Courier New">Courier New</option>
       <option value="Georgia">Georgia</option>
  <option value="Lato">Lato</option>
  <option value="Montserrat">Montserrat</option>
  <option value="Verdana">Verdana</option>
    </select>
  </label>
  <label>
  Background
  <input type="color" v-model="fontBgColor" @input="updateFontBgColor" />
</label>

<label>
  Border Color
  <input type="color" v-model="fontStrokeColor" @input="updateFontStroke" />
</label>

<label>
  Border Width
  <input
    type="number"
    min="0"
    max="10"
    v-model="fontStrokeWidth"
    @input="updateFontStroke"
  />
</label>

<button @click="toggleShadow" :class="{ active: hasShadow }">Shadow</button>


  </div>

  <div class="toolbar-row">
    <button @click="toggleBold" :class="{ active: isBold }">B</button>
    <button @click="toggleItalic" :class="{ active: isItalic }">I</button>
    <button class="delete-btn" @click="closeToolbar">×</button>
  </div>
</div>



  </div>
</template>

<script setup>
import { ref, onMounted, watchEffect, nextTick, onBeforeUnmount, computed } from 'vue'
import * as fabric from 'fabric'
import { debounce } from 'lodash-es'

const props = defineProps({
  width: {
    type: Number,
    default: 500
  },
  height: {
    type: Number,
    default: 500
  },
  backgroundImage: String,
  profileImage: String,
  name: String,
  post: String,
  description: String,
  phone: String,
  title: String,
  subtitle: String
})

const canvasRef = ref()
let canvas
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)

// Responsive canvas dimensions
const canvasWidth = computed(() => {
  const baseWidth = props.width
  if (windowWidth.value <= 768) {
     return  500
  } else if (windowWidth.value <= 1024) {
    return 580
  }
  return 580
})

const canvasHeight = computed(() => {
  const baseHeight = props.height
  if (windowWidth.value <= 768) {
    return 500;
  } else if (windowWidth.value <= 1024) {
    return 580
  }
  return 580
})
const debouncedUpdateFontSize = debounce(() => {
  if (selectedText.value) {
    selectedText.value.set('fontSize', parseInt(fontSize.value))
    canvas.requestRenderAll()
  }
}, 300)

// Toolbar state
const showToolbar = ref(false)
const selectedText = ref(null)
const toolbarX = ref(0)
const toolbarY = ref(0)
const fontSize = ref(28)
const fontColor = ref('#000000')
const isBold = ref(false)
const isItalic = ref(false)
const undoStack = ref([])
const redoStack = ref([])
const fileInputRef = ref()
let profileImageObj = null
const showProfileMenu = ref(false)
const profileMenuRef = ref(null)
const menuX = ref(0)
const menuY = ref(0)
const nameFontSize = windowWidth.value < 768 ? 18 : 22
const postFontSize = nameFontSize - 2
const descFontSize = postFontSize - 2
const phoneFontSize = windowWidth.value < 768 ? 14 : 16
// Add these with other refs
const fontBgColor = ref('#ffffff')
const fontStrokeColor = ref('#000000')
const fontStrokeWidth = ref(0)
const hasShadow = ref(false)
let logoImageObj = null



// Update background color
function updateFontBgColor() {
  if (selectedText.value) {
    selectedText.value.set('backgroundColor', fontBgColor.value)
    canvas.requestRenderAll()
  }
}

// Update stroke/border
function updateFontStroke() {
  if (selectedText.value) {
    selectedText.value.set({
      stroke: fontStrokeColor.value,
      strokeWidth: parseInt(fontStrokeWidth.value)
    })
    canvas.requestRenderAll()
  }
}

// Toggle text shadow
function toggleShadow() {
  if (!selectedText.value) return
  hasShadow.value = !hasShadow.value
  selectedText.value.set(
    'shadow',
    hasShadow.value ? '2px 2px 4px rgba(0,0,0,0.4)' : null
  )
  canvas.requestRenderAll()
}


function handleResize() {
  windowWidth.value = window.innerWidth
  if (canvas) {
    // Use nextTick to ensure DOM updates
    nextTick(() => {
      canvas.setDimensions({
        width: canvasWidth.value,
        height: canvasHeight.value
      })
      // Re-render canvas content with new dimensions
      renderCanvas()
    })
  }
}


function handleClickOutside(event) {
  if (
    showProfileMenu.value &&
    profileMenuRef.value &&
    !profileMenuRef.value.contains(event.target)
  ) {
    showProfileMenu.value = false
  }
}

function triggerProfileUpload() {
  showProfileMenu.value = false
  fileInputRef.value?.click()
}

function saveState() {
  const json = canvas.toJSON()
  undoStack.value.push(JSON.stringify(json))
  redoStack.value = [] // clear redo stack on new action
}
function undo() {
  if (undoStack.value.length > 0) {
    const state = undoStack.value.pop()
    redoStack.value.push(JSON.stringify(canvas.toJSON()))
    canvas.loadFromJSON(JSON.parse(state), () => canvas.renderAll())
  }
}

function redo() {
  if (redoStack.value.length > 0) {
    const state = redoStack.value.pop()
    undoStack.value.push(JSON.stringify(canvas.toJSON()))
    canvas.loadFromJSON(JSON.parse(state), () => canvas.renderAll())
  }
}
let dragOffsetX = 0
let dragOffsetY = 0

function startDrag(e) {
  const point = e.type.includes('touch') ? e.touches[0] : e

  dragOffsetX = point.clientX - toolbarX.value
  dragOffsetY = point.clientY - toolbarY.value

  document.addEventListener('mousemove', dragToolbar)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', dragToolbar, { passive: false })
  document.addEventListener('touchend', stopDrag)
}

function dragToolbar(e) {
  const point = e.type.includes('touch') ? e.touches[0] : e

  // Prevent page scroll while dragging on mobile
  if (e.cancelable) e.preventDefault()

  toolbarX.value = point.clientX - dragOffsetX
  toolbarY.value = point.clientY - dragOffsetY

  // Optional: constrain inside window
  const maxX = window.innerWidth - 280
  const maxY = window.innerHeight - 100
  toolbarX.value = Math.max(0, Math.min(toolbarX.value, maxX))
  toolbarY.value = Math.max(0, Math.min(toolbarY.value, maxY))
}

function stopDrag() {
  document.removeEventListener('mousemove', dragToolbar)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', dragToolbar)
  document.removeEventListener('touchend', stopDrag)
}


const fontFamily = ref('Arial')

function updateFontFamily() {
  if (selectedText.value) {
    selectedText.value.set('fontFamily', fontFamily.value)
    canvas.requestRenderAll()
  }
}

onMounted(async () => {
  // Wait for DOM to be ready
  await nextTick()
  
  canvas = new fabric.Canvas(canvasRef.value, {
    width: canvasWidth.value,
    height: canvasHeight.value
  })

  // Handle selection
  canvas.on('selection:created', handleSelection)
  canvas.on('selection:updated', handleSelection)

  canvas.on('mouse:down', (e) => {
    if (!e.target) {
      selectedText.value = null
      showToolbar.value = false
    }
  })
  
  document.addEventListener('mousedown', handleClickOutside)
  window.addEventListener('resize', handleResize)
  
  // Initial render
  await nextTick()
  renderCanvas()
})

// Watch for prop changes and re-render
watchEffect(async () => {
  if (canvas && isInitialized) {
    // Only re-render if we have actual content to show
    const hasContent = props.name || props.post || props.description || props.phone || props.backgroundImage || props.profileImage
    if (hasContent) {
      await nextTick()
      renderCanvas()
    }
  }
})

onBeforeUnmount(() => {
  if (canvas) {
    canvas.dispose()
  }
  document.removeEventListener('mousedown', handleClickOutside)
  window.removeEventListener('resize', handleResize)
})

// Initial setup flag
let isInitialized = false
watchEffect(() => {
  if (!isInitialized && canvasWidth.value && canvasHeight.value && canvas) {
    isInitialized = true
    renderCanvas() // Initial render
  }
})

function closeToolbar() {
  showToolbar.value = false;
  selectedText.value = null;
  canvas.discardActiveObject();
  canvas.requestRenderAll();
}

function handleSelection(e) {
  const obj = e.selected?.[0]
  if (obj?.type !== 'textbox') return

  selectedText.value = obj
  fontSize.value = obj.fontSize || 20
  fontColor.value = obj.fill || '#000000'
  fontFamily.value = obj.fontFamily || 'Arial'
  isBold.value = obj.fontWeight === 'bold'
  isItalic.value = obj.fontStyle === 'italic'
  fontBgColor.value = obj.backgroundColor || '#ffffff'
fontStrokeColor.value = obj.stroke || '#000000'
fontStrokeWidth.value = obj.strokeWidth || 0
hasShadow.value = !!obj.shadow


  const bound = obj.getBoundingRect()
  const canvasRect = canvasRef.value.getBoundingClientRect()
  const toolbarWidth = 280
  const toolbarHeight = 70

  let newX = bound.left
  let newY = bound.top + bound.height + 10

  // Flip toolbar above if not enough space
  if (bound.top + bound.height + toolbarHeight > canvasHeight.value && bound.top > toolbarHeight + 10) {
    newY = bound.top - toolbarHeight - 10
  }

  // Keep toolbar inside canvas width
  newX = Math.max(10, Math.min(newX, canvasWidth.value - toolbarWidth - 10))
  newY = Math.max(10, Math.min(newY, canvasHeight.value - toolbarHeight - 10))

  toolbarX.value = newX
  toolbarY.value = newY
  showToolbar.value = true
}


function updateFontSize() {
  if (selectedText.value) {
    selectedText.value.set('fontSize', parseInt(fontSize.value))
    canvas.requestRenderAll()
  }
}

function updateFontColor() {
  if (selectedText.value) {
    selectedText.value.set('fill', fontColor.value)
    canvas.requestRenderAll()
  }
}

function deleteText() {
  if (selectedText.value) {
    canvas.remove(selectedText.value)
    selectedText.value = null
    showToolbar.value = false
    canvas.requestRenderAll()
  }
}

function toggleBold() {
  if (!selectedText.value) return
  isBold.value = !isBold.value
  selectedText.value.set('fontWeight', isBold.value ? 'bold' : 'normal')
  canvas.requestRenderAll()
}

function toggleItalic() {
  if (!selectedText.value) return
  isItalic.value = !isItalic.value
  selectedText.value.set('fontStyle', isItalic.value ? 'italic' : 'normal')
  canvas.requestRenderAll()
}

function duplicateText() {
  if (!selectedText.value) return
  selectedText.value.clone((cloned) => {
    cloned.set({
      left: (selectedText.value.left || 0) + 20,
      top: (selectedText.value.top || 0) + 20,
      editable: true
    })
    canvas.add(cloned)
    canvas.setActiveObject(cloned)
    selectedText.value = cloned
    canvas.requestRenderAll()
  })
}


function loadFabricImage(url, options = {}) {
  return new Promise((resolve) => {
    if (!url) return resolve(null)
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.src = url
    img.onload = () => {
      const fabricImg = new fabric.Image(img, options)
      resolve(fabricImg)
    }
    img.onerror = () => resolve(null)
  })
}

async function renderCanvas() {
  if (!canvas) return;

  canvas.clear();

  canvas.setDimensions({
    width: canvasWidth.value,
    height: canvasHeight.value
  });
const isMobile = windowWidth.value < 480
  const baseFontSize = isMobile ? 13 : 16
  const nameSize = baseFontSize + 2
  const postSize = baseFontSize
  const descSize = baseFontSize - 1
  // Background Image
  const bgImage = await loadFabricImage(props.backgroundImage);
  if (bgImage) {
    bgImage.set({
      left: 0,
      top: 0,
      scaleX: canvasWidth.value / bgImage.width,
      scaleY: canvasHeight.value / bgImage.height,
      selectable: false,
      evented: false
    });
    canvas.add(bgImage);
  }

// Load logo image and apply circular clip

const logoSize = windowWidth.value < 768 ? 60 : 90
const logoUrl = '/templates/logo.png' // replace with actual static path

const logoImg = await loadFabricImage(logoUrl)

if (logoImg) {
  // Calculate scale so the entire image fits inside the circle
  const scale = logoSize / Math.max(logoImg.width, logoImg.height)

  // Set image properties
  logoImg.set({
    scaleX: scale,
    scaleY: scale,
    originX: 'center',
    originY: 'center',
    left: 0,
    top: 0,
    selectable: false,
    evented: false
  })

  // Create circular frame behind the image
  const circle = new fabric.Circle({
    radius: logoSize / 2,
    fill: '#fff',
    stroke: '#222',
    strokeWidth: 2,
    originX: 'center',
    originY: 'center',
    left: 0,
    top: 0,
    selectable: false,
    evented: false
  })

  // Group both to form one draggable + resizable unit
  const logoGroup = new fabric.Group([circle, logoImg], {
    left: 30,
    top: 30,
    hasControls: true,
    lockScalingFlip: true,
    cornerColor: '#0E5D39',
    cornerSize: windowWidth.value < 768 ? 12 : 10,
    hoverCursor: 'move'
  })

  canvas.add(logoGroup)
}



  // ── Editable Phone (Top Right) ──
  if (props.phone) {
    const phoneText = `📞 ${props.phone}`
    const phoneFontSize = baseFontSize

    const text = new fabric.Textbox(phoneText, {
      left: canvasWidth.value - 10,
      top: 15,
      fontSize: phoneFontSize,
      fontWeight: 'normal',
      fontFamily: 'Arial',
      fill: '#000',
      textAlign: 'right',
      originX: 'right',
      editable: true
    })

    canvas.add(text)
  }


    // ── Centered Title & Subtitle ──
  const titleFontSize = isMobile ? 22 : 32
  const subtitleFontSize = isMobile ? 16 : 24

 
addCenteredText(
  props.title?.trim() ,
  canvasHeight.value / 2 - titleFontSize,
  titleFontSize,
  {
    fontWeight: 'bold',
    fill: '#222',
    fontFamily: 'Arial'
  }
)

addCenteredText(
  props.subtitle?.trim(),
  canvasHeight.value / 2 + 10,
  subtitleFontSize,
  {
    fontWeight: 'normal',
    fill: '#222',
    fontFamily: 'Arial'
  }
)


  // ── Profile Image (Bottom Right) ──
   const profileSize = isMobile ? 80 : 120
  const scale = profileSize / 300 
  const profileImg = await loadFabricImage(props.profileImage);
  if (profileImg) {
    const scale = windowWidth.value < 768 ? 0.15 : 0.25;
    //const profileSize = windowWidth.value < 768 ? 100 : 150;

    profileImg.set({
      left: canvasWidth.value - profileSize - 20,
      top: canvasHeight.value - profileSize - 15,
      scaleX: scale,
      scaleY: scale,
      hasControls: true,
      hoverCursor: 'pointer'
    });

    profileImg.on('mousedown', (event) => {
      const pointer = canvas.getPointer(event.e);
      let newX = pointer.x + 20;
      let newY = pointer.y + 20;

      if (newX + 200 > canvasWidth.value) newX = pointer.x - 200;
      if (newY + 50 > canvasHeight.value) newY = pointer.y - 50;

      menuX.value = Math.max(0, newX);
      menuY.value = Math.max(0, newY);
      showProfileMenu.value = true;
      fileInputRef.value.dataset.uploadType = 'profile';
    });

    profileImageObj = profileImg;
    canvas.add(profileImg);
  }

  

  // ── Bottom Left Texts ──
  const nameFontSize = windowWidth.value < 768 ? 18 : 22;
  const postFontSize = nameFontSize - 2;
  const descFontSize = postFontSize - 2;
  let bottomY = canvasHeight.value - 40;

  if (props.description?.trim()) {
    addText(props.description, 20, bottomY, 'Your Description', descFontSize);
    bottomY -= descFontSize + 10;
  }

  if (props.post?.trim()) {
    addText(props.post, 20, bottomY, 'Your Post', postFontSize);
    bottomY -= postFontSize + 8;
  }

  if (props.name?.trim()) {
    addText(props.name, 20, bottomY, 'Your Name', nameFontSize);
  }

  canvas.renderAll();
}

function addCenteredText(text, y, fontSize = 24, options = {}) {
  const textbox = new fabric.Textbox(text, {
    left: canvasWidth.value / 2,
    top: y,
    fontSize,
    fontFamily: options.fontFamily || 'Noto Sans Devanagari, Arial',
    fill: options.fill || '#000000',
    fontWeight: options.fontWeight || 'normal',
    textAlign: 'center',
    originX: 'center',
    editable: true,
    hasControls: true,
    width: canvasWidth.value * 0.8
  })
  canvas.add(textbox)
}


function addText(value, x, y, placeholder, size = 20) {
  if (!value || !value.trim()) return

  const textbox = new fabric.Textbox(value.trim(), {
    left: x,
    top: y,
    fontSize: size,
    fill: '#000000',
    fontWeight: 'normal', // default non-bold
    fontStyle: 'normal',
    fontFamily: 'Arial',
    editable: true,
    hasControls: true,
    lockScalingFlip: true,
    lockUniScaling: false,
    borderColor: '#666',
    cornerColor: '#0E5D39',
    cornerSize: windowWidth.value < 768 ? 12 : 8,
    transparentCorners: false,
    width: Math.min(canvasWidth.value - x - 20, 300),
    splitByGrapheme: false
  })

  canvas.add(textbox)
}

function exportAsPNG() {
  if (!canvas) return
  const dataURL = canvas.toDataURL({
    format: 'png',
    quality: 1
  })

  const base64 = dataURL.split(",")[1];
    if (window.AndroidInterface && window.AndroidInterface.saveBase64Image) {
    window.AndroidInterface.saveBase64Image(base64);
    // Optionally show a toast or confirm to the user
  } else {
  // Download automatically
  const link = document.createElement('a')
  link.href = dataURL
  link.download = 'poster.png'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
}

async function sharePoster() {
  if (!canvas) {
    alert("Canvas not ready.")
    return
  }

  const dataUrl = canvas.toDataURL({
    format: 'png',
    quality: 1.0,
    multiplier: 2 // optional for higher resolution
  })

  const message = "Check out this poster I made!";
  const subject = "My Poster";

   if (window.AndroidInterface && window.AndroidInterface.shareText) {
    window.AndroidInterface.shareText(message, subject);
    return;
  }

  // Convert dataURL to Blob
  const blob = await fetch(dataUrl).then(res => res.blob())

  if (!blob) {
    alert('Unable to generate image.')
    return
  }

  const file = new File([blob], 'poster.png', { type: 'image/png' })

  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({
        title:  subject,
        text: message,
        files: [file]
      })
    } catch (err) {
      console.error('Share failed:', err)
      alert('Sharing failed. Please try again.')
    }
  } else {
    alert('Sharing not supported on this device.')
  }
}



function handleProfileChange(e) {
  const file = e.target.files[0]
  if (!file) return

  const uploadType = fileInputRef.value.dataset.uploadType || 'profile'

  const reader = new FileReader()
  reader.onload = () => {
    const img = new Image()
    img.src = reader.result
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const scale = windowWidth.value < 768 ? 0.15 : 0.25
      const profileSize = windowWidth.value < 768 ? 100 : 150

      const newImg = new fabric.Image(img, {
        left: uploadType === 'profile'
          ? profileImageObj?.left || canvasWidth.value - profileSize
          : 20,
        top: uploadType === 'profile'
          ? profileImageObj?.top || canvasHeight.value - profileSize
          : 20,
        scaleX: scale,
        scaleY: scale,
        hasControls: true,
        hoverCursor: 'pointer'
      })

      if (uploadType === 'profile') {
        newImg.on('mousedown', (event) => {
          const pointer = canvas.getPointer(event.e)
          let newX = pointer.x + 20
          let newY = pointer.y + 20

          if (newX + 200 > canvasWidth.value) newX = pointer.x - 200
          if (newY + 50 > canvasHeight.value) newY = pointer.y - 50

          menuX.value = Math.max(0, newX)
          menuY.value = Math.max(0, newY)
          showProfileMenu.value = true
          fileInputRef.value.dataset.uploadType = 'profile'
        })

        if (profileImageObj) canvas.remove(profileImageObj)
        profileImageObj = newImg
      } else {
        if (logoImageObj) canvas.remove(logoImageObj)
        logoImageObj = newImg
      }

      canvas.add(newImg)
      canvas.setActiveObject(newImg)
      canvas.renderAll()
    }
  }

  reader.readAsDataURL(file)
}
defineExpose({
  exportAsPNG,
  sharePoster
})

</script>

<style scoped>
.canvas-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  box-sizing: border-box;
}

.hidden-input {
  display: none;
}

.poster-canvas {
  display: block;
  max-width: 100%;
  max-height: 100vh;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.profile-context-menu {
  position: absolute;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 8px 12px;
  z-index: 1000;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.2s ease-in-out;
}

.profile-context-menu button {
  background-color: #0e5d39;
  color: #fff;
  font-size: 14px;
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.profile-context-menu button:hover {
  background-color: #09472b;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.floating-toolbar {
  position: absolute;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #ffffff;
  border: 1px solid #ccc;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  padding: 12px;
  z-index: 20;
  min-width: 280px;
  max-width: 90vw;
  transition: all 0.2s ease;
}

.toolbar-row {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.floating-toolbar label {
  font-size: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  min-width: 60px;
}

.floating-toolbar select {
  font-size: 12px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  border-radius: 3px;
  max-width: 100px;
}

.floating-toolbar input[type='number'] {
  width: 50px;
  font-size: 12px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  border-radius: 3px;
}

.floating-toolbar input[type='color'] {
  width: 36px;
  height: 24px;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
}

.floating-toolbar button {
  background: #f0f0f0;
  border: 1px solid #bbb;
  padding: 6px 10px;
  font-size: 14px;
  border-radius: 5px;
  cursor: pointer;
  min-width: 36px;
}

.floating-toolbar button.active {
  background: #1976d2;
  color: white;
  font-weight: bold;
}

.delete-btn {
  background: #e53935 !important;
  color: #fff;
  font-weight: bold;
}
.drag-handle {
  cursor: move;
  background-color: #f6f6f6;
  border-bottom: 1px solid #ddd;
  border-radius: 6px 6px 0 0;
  padding: 4px 6px;
}





/* Mobile specific styles */
@media (max-width: 768px) {
  .canvas-wrapper {
    padding: 2px;
  }
  
  .floating-toolbar {
    min-width: 260px;
    max-width: calc(100vw - 20px);
    font-size: 12px;
  }
  
  .toolbar-row {
    gap: 6px;
  }
  
  .floating-toolbar label {
    font-size: 11px;
    min-width: 50px;
  }
  
  .floating-toolbar select {
    font-size: 11px;
    max-width: 80px;
  }
  
  .floating-toolbar input[type='number'] {
    width: 40px;
    font-size: 11px;
  }
  
  .floating-toolbar button {
    padding: 4px 8px;
    font-size: 12px;
    min-width: 32px;
  }
  
  .profile-context-menu {
    font-size: 12px;
    padding: 6px 8px;
  }
  
  .profile-context-menu button {
    font-size: 12px;
    padding: 4px 8px;
  }
   .modal-footer {
    flex-direction: column;
    align-items: stretch;
  }

 
}

@media (max-width: 480px) {
  .floating-toolbar {
    min-width: 240px;
    padding: 8px;
  }
  
  .toolbar-row {
    gap: 4px;
  }
  
  .floating-toolbar label {
    font-size: 10px;
    min-width: 45px;
  }
  
  .floating-toolbar select {
    font-size: 10px;
    max-width: 70px;
  }
  
  .floating-toolbar input[type='number'] {
    width: 35px;
    font-size: 10px;
  }
  
  .floating-toolbar button {
    padding: 3px 6px;
    font-size: 11px;
    min-width: 28px;
  }
}
</style>