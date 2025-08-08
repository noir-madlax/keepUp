<template>
  <!-- Floating AI ask button (desktop only) -->
  <div 
    v-if="!isMobile && chatStore.chatWindowState === 'minimized'"
    class="fixed right-10 top-[110px] z-[1002] select-none"
  >
    <button
      type="button"
      class="relative group"
      @click="openChat"
      aria-label="Ask KeepUp Anything"
    >
      <!-- neon outer glow (static, no pulse) -->
      <div class="absolute -inset-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 opacity-70 blur-lg group-hover:opacity-90 transition-opacity"></div>

      <!-- pill content -->
      <div
        class="relative flex items-center gap-0 px-4 py-2.5 rounded-full text-white shadow-xl ring-1 ring-white/10 overflow-hidden transition transform group-hover:-translate-y-0.5 holo-pill"
      >
        <!-- sweeping shine -->
        <span class="shine" aria-hidden="true"></span>

        <!-- label -->
        <span class="text-[12px] sm:text-[13px] font-semibold tracking-wide drop-shadow-[0_1px_1px_rgba(0,0,0,0.25)] whitespace-nowrap">Ask KeepUp</span>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const isMobile = computed(() => typeof window !== 'undefined' && window.innerWidth <= 768)

const openChat = () => {
  if (chatStore.chatWindowState !== 'expanded') {
    chatStore.chatWindowState = 'expanded'
  }
}
</script>

<style scoped>
/* neon gradient pill */
.holo-pill {
  background: linear-gradient(90deg, #7c3aed 0%, #db2777 50%, #7c3aed 100%);
  background-size: 300% 300%;
  animation: gradient-flow 18s ease infinite, float-y 12s ease-in-out infinite;
}

@keyframes gradient-flow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* subtle floating effect */
@keyframes float-y {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

/* outer pulse disabled per request */

/* sweeping light */
.shine {
  position: absolute;
  inset: 0;
  left: -40%;
  width: 40%;
  background: linear-gradient(120deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.35) 30%, rgba(255,255,255,0.12) 60%, rgba(255,255,255,0) 100%);
  transform: skewX(-20deg);
  animation: shine-move 9.6s ease-in-out infinite;
}

@keyframes shine-move {
  0% { transform: translateX(0) skewX(-20deg); }
  100% { transform: translateX(250%) skewX(-20deg); }
}
</style>


