<script setup>
import { useI18n } from 'vue-i18n'
import { Server, Play } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  subdomains: { type: Array, required: true },
  domain: { type: String, required: true }
})
</script>

<template>
  <div class="result-card glass-panel subdomains-card">
    <div class="card-header">
      <Server size="20" class="text-blue" />
      <h3>{{ t('targetComponents.subdomains.title') }}</h3>
    </div>

    <div class="card-body">
      <div v-if="!subdomains || subdomains.length === 0" class="empty-msg">
        {{ t('targetComponents.subdomains.empty') }}
      </div>

      <div v-else class="scrollable">
        <div class="count-badge mb-2">
          {{ t('targetComponents.subdomains.found', { count: subdomains.length }) }}
        </div>
        <div class="domains-list">
          <div v-for="sub in subdomains" :key="sub" class="domain-item">
            <Play size="12" class="text-blue arrow-icon" />
            <a :href="`https://${sub}`" target="_blank" rel="noopener noreferrer" class="path mono truncate" :title="sub">{{ sub }}</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.subdomains-card { display: flex; flex-direction: column; }
.scrollable { max-height: 250px; overflow-y: auto; padding-right: 8px; }
.count-badge { font-size: 0.8rem; color: var(--text-muted); font-weight: 500; }
.mb-2 { margin-bottom: 12px; }
.domains-list { display: flex; flex-direction: column; gap: 8px; }
.domain-item { display: flex; align-items: center; gap: 8px; }
.arrow-icon { flex-shrink: 0; }
.path { color: var(--text-main); font-size: 0.85rem; text-decoration: none; transition: color 0.2s; display: block; padding: 2px 0; }
.path:hover { color: var(--accent-blue); text-decoration: underline; }
.truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
.empty-msg { font-size: 0.85rem; color: var(--text-muted); font-style: italic; }
</style>
