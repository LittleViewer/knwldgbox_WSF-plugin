<script setup>
import { Globe, Link } from 'lucide-vue-next'

defineProps({
  urlscan: { type: Object, required: true }
})
</script>

<template>
  <div class="result-card glass-panel screenshot-card">
    <div class="card-header">
      <Globe size="18" class="text-blue" />
      <h3>Visual Footprint</h3>
    </div>
    <div class="card-body">
      <a :href="urlscan.result" target="_blank" class="screenshot-wrapper">
        <img :src="urlscan.screenshot" alt="Website Screenshot" class="urlscan-screenshot" />
        <div class="overlay-link">
          <Link size="16" /> View Full Report on urlscan.io
        </div>
      </a>
    </div>
  </div>
</template>

<style scoped>
.result-card {
  padding: 20px;

  display: flex;
  flex-direction: column;
}

.screenshot-card {
  grid-row: span 2;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.screenshot-wrapper {
  display: block;
  position: relative;

  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
}

.screenshot-wrapper:hover {
  border-color: var(--accent-orange);
}

.urlscan-screenshot {
  width: 100%;
  display: block;
  object-fit: cover;
}

.overlay-link {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--accent-orange);
  font-weight: 600;
  transform: translateY(100%);
  transition: transform 0.2s ease;
}

.screenshot-wrapper:hover .overlay-link {
  transform: translateY(0);
}

.text-blue {
  color: var(--accent-blue);
}
</style>
