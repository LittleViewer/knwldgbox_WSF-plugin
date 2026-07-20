<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { Lock, ShieldAlert, ShieldCheck } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
  ssl: { type: Object, required: true }
})

const isValid = computed(() => props.ssl.days_remaining > 0)
</script>

<template>
  <div class="result-card glass-panel ssl-card">
    <div class="card-header">
      <Lock size="20" :class="isValid ? 'text-green' : 'text-red'" />
      <h3>{{ t('targetAnalysis.components.ssl.title') }}</h3>
    </div>
    
    <div class="card-body">
      <div class="status-banner" :class="isValid ? 'valid' : 'invalid'">
        <component :is="isValid ? ShieldCheck : ShieldAlert" size="18" />
        <span>{{ isValid ? `Valid for ${ssl.days_remaining} days` : 'Expired or Invalid' }}</span>
      </div>

      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.ssl.issuer') }}</span>
        <span class="value">{{ ssl.issuer }}</span>
      </div>
      
      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.ssl.subject') }}</span>
        <span class="value">{{ ssl.subject }}</span>
      </div>
      
      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.ssl.validFrom') }}</span>
        <span class="value mono text-sm">{{ ssl.valid_from.split('T')[0] }}</span>
      </div>
      
      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.ssl.validTo') }}</span>
        <span class="value mono text-sm">{{ ssl.valid_to.split('T')[0] }}</span>
      </div>
      
      <div class="data-row stack" v-if="ssl.sans && ssl.sans.length > 0">
        <span class="label">{{ t('targetAnalysis.components.ssl.sans') }}</span>
        <div class="sans-list">
          <span v-for="san in ssl.sans" :key="san" class="san-badge mono">{{ san }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ssl-card {
  display: flex;
  flex-direction: column;
}

.status-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;

  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 12px;
}

.status-banner.valid {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-green);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-banner.invalid {
  background: rgba(239, 68, 68, 0.1);
  color: var(--accent-red);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.text-sm {
  font-size: 0.8rem !important;
}

.sans-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.san-badge {
  font-size: 0.75rem;
  background: var(--overlay-5);
  border: 1px solid var(--overlay-10);
  padding: 2px 6px;

  color: var(--text-main);
}
</style>
