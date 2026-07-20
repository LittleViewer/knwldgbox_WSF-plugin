<script setup>
import { MapPin } from 'lucide-vue-next'

const props = defineProps({
  geo: { type: Object, required: true }
})
</script>

<template>
  <div class="result-card glass-panel geo-card">
    <div class="card-header">
      <MapPin size="20" class="text-green" />
      <h3>Server Location</h3>
    </div>
    
    <div class="card-body">
      <div v-if="!geo.country" class="empty-msg">
        Geolocation data unavailable.
      </div>
      
      <template v-else>
        <div class="data-row">
          <span class="label">IP Address</span>
          <span class="value mono">{{ geo.ip }}</span>
        </div>
        
        <div class="data-row">
          <span class="label">Location</span>
          <span class="value">{{ geo.city }}, {{ geo.country }}</span>
        </div>
        
        <div class="data-row">
          <span class="label">Coordinates</span>
          <span class="value mono text-muted">{{ geo.lat }}, {{ geo.lon }}</span>
        </div>
        
        <div class="data-row mt-2">
          <span class="label">ISP</span>
          <span class="value">{{ geo.isp || 'Unknown' }}</span>
        </div>
        
        <div class="data-row">
          <span class="label">Organization</span>
          <span class="value">{{ geo.org || 'Unknown' }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.geo-card { display: flex; flex-direction: column; }
.mt-2 { margin-top: 8px; border-top: 1px solid var(--overlay-5); padding-top: 12px; }
.text-muted { color: var(--text-muted); font-size: 0.85rem; }
.empty-msg { font-size: 0.85rem; color: var(--text-muted); font-style: italic; }
</style>
