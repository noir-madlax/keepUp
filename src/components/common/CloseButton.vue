<template>
  <button 
    @click="$emit('click')"
    class="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
  >
    <span class="sr-only">Close</span>
    <svg class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
    </svg>
  </button>
</template>

<script setup lang="ts">
defineEmits(['click'])
</script> 