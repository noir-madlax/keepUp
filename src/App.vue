<template>
  <offline-alert />
  <router-view></router-view>
  <pwa-update-popup />
</template>

<script setup lang="ts">
import PWAUpdatePopup from './components/PWAUpdatePopup.vue'
import OfflineAlert from './components/OfflineAlert.vue'
</script>
