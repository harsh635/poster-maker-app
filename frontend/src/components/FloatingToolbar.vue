<template>
  <div
    v-if="visible"
    class="floating-toolbar"
    :style="{ top: `${position.y}px`, left: `${position.x}px` }"
  >
    <!-- Font Size Controls -->
    <div class="toolbar-group">
      <button @click="decreaseFontSize">A-</button>
      <span>{{ fontSize }}</span>
      <button @click="increaseFontSize">A+</button>
    </div>

    <!-- Color Picker -->
    <div class="toolbar-group">
      <input type="color" v-model="color" @input="emitColorChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  visible: Boolean,
  position: Object,
  selectedField: Object
})

const emit = defineEmits(['update:selectedField'])

const fontSize = computed(() => props.selectedField?.fontSize || 18)
const color = ref(props.selectedField?.color || '#ffffff')

watch(() => props.selectedField?.color, newColor => {
  color.value = newColor || '#ffffff'
})

function increaseFontSize() {
  updateField({ fontSize: fontSize.value + 2 })
}

function decreaseFontSize() {
  if (fontSize.value > 8) {
    updateField({ fontSize: fontSize.value - 2 })
  }
}

function emitColorChange() {
  updateField({ color: color.value })
}

function updateField(changes) {
  if (!props.selectedField) return
  emit('update:selectedField', {
    ...props.selectedField,
    ...changes
  })
}
</script>

<style scoped>
.floating-toolbar {
  position: absolute;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 6px 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 2000;
  display: flex;
  gap: 10px;
  align-items: center;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar-group button {
  background-color: #eee;
  border: none;
  padding: 4px 8px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
}

.toolbar-group button:hover {
  background-color: #ddd;
}

.toolbar-group input[type='color'] {
  border: none;
  width: 32px;
  height: 32px;
  padding: 0;
}
</style>
