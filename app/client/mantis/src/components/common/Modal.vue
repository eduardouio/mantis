<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'lg', // sm, md, lg, xl, 2xl
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl'].includes(value)
  }
})

const emit = defineEmits(['close'])

const closeModal = () => {
  emit('close')
}

const sizeClasses = {
  sm: 'modal-box w-11/12 max-w-md',
  md: 'modal-box w-11/12 max-w-2xl',
  lg: 'modal-box w-11/12 max-w-4xl',
  xl: 'modal-box w-11/12 max-w-6xl',
  '2xl': 'modal-box w-11/12 max-w-7xl'
}
</script>

<template>
  <div class="modal" :class="{ 'modal-open': isOpen }">
    <div :class="sizeClasses[size]">
      <!-- Header del Modal -->
      <div class="flex justify-between items-center mb-4 pb-3 border-b-2 border-blue-300" v-if="title">
        <h3 class="text-lg font-semibold text-gray-700">{{ title }}</h3>
        <button 
          class="btn btn-sm btn-circle btn-ghost" 
          @click="closeModal"
        >
          ✕
        </button>
      </div>
      
      <!-- Contenido del Modal -->
      <div class="modal-content">
        <slot></slot>
      </div>
    </div>
    
    <!-- Backdrop -->
    <div class="modal-backdrop" @click="closeModal"></div>
  </div>
</template>
