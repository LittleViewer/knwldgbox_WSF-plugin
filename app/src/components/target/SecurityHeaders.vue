<script setup>
import { useI18n } from 'vue-i18n'
import { Shield, CheckCircle2, XCircle } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  headers: { type: Object, required: true }
})

// Essential security headers to check
const essentialHeaders = [
  'Strict-Transport-Security',
  'Content-Security-Policy',
  'X-Frame-Options',
  'X-Content-Type-Options',
  'Referrer-Policy'
]

const infoHeaders = [
  'Server',
  'X-Powered-By'
]
</script>

<template>
  <div class="result-card glass-panel headers-card">
    <div class="card-header">
      <Shield size="20" class="text-purple" />
      <h3>{{ t('targetComponents.securityHeaders.title') }}</h3>
    </div>

    <div class="card-body">
      <div class="headers-section">
        <div v-for="key in essentialHeaders" :key="key" class="header-row">
          <span class="label truncate" :title="key">{{ key }}</span>
          <div class="status-indicator">
            <CheckCircle2 size="16" class="text-green" v-if="headers[key]" />
            <XCircle size="16" class="text-red" v-else />
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="headers-section">
        <div v-for="key in infoHeaders" :key="key" class="data-row stack">
          <span class="label">{{ key }}</span>
          <span class="value mono text-sm">{{ headers[key] || t('targetComponents.securityHeaders.notExposed') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.headers-card {
  display: flex;
  flex-direction: column;
}

.headers-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background: var(--overlay-2);

  border: 1px solid var(--overlay-5);
}

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80%;
  font-size: 0.85rem;
  color: var(--text-main);
}

.divider {
  height: 1px;
  background: var(--overlay-10);
  margin: 12px 0;
}

.text-sm {
  font-size: 0.8rem !important;
  color: var(--accent-orange) !important;
}

.stack {
  background: var(--overlay-2);
  padding: 8px 12px;

}
</style>
