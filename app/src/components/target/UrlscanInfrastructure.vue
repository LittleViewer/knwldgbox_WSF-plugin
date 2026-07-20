<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { Server } from 'lucide-vue-next'
import SendToGraphButton from '../SendToGraphButton.vue'

defineProps({
  urlscan: { type: Object, required: true }
})
</script>

<template>
  <div class="result-card glass-panel">
    <div class="card-header">
      <Server size="18" class="text-orange" />
      <h3>{{ t('targetAnalysis.components.infra.title') }}</h3>
    </div>
    <div class="card-body">
      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.infra.primaryIp') }}</span>
        <div class="val-group">
          <span class="value highlight">{{ urlscan.page?.ip || 'N/A' }}</span>
          <SendToGraphButton small :label="urlscan.page?.ip" iconName="Server" color="#F97316" notes="Primary IP" v-if="urlscan.page?.ip" />
        </div>
      </div>
      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.infra.server') }}</span>
        <div class="val-group">
          <span class="value">{{ urlscan.page?.server || 'N/A' }}</span>
          <SendToGraphButton small :label="urlscan.page?.server" iconName="Database" color="#8B5CF6" notes="Web Server" v-if="urlscan.page?.server" />
        </div>
      </div>
      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.infra.asn') }}</span>
        <div class="val-group">
          <span class="value">{{ urlscan.page?.asnname || 'N/A' }}</span>
          <SendToGraphButton small :label="urlscan.page?.asnname" iconName="Building" color="#3B82F6" notes="ASN" v-if="urlscan.page?.asnname" />
        </div>
      </div>
      <div class="data-row">
        <span class="label">{{ t('targetAnalysis.components.infra.hostingCountry') }}</span>
        <div class="val-group">
          <span class="value">{{ urlscan.page?.country || 'N/A' }}</span>
          <SendToGraphButton small :label="urlscan.page?.country" iconName="Globe" color="#10B981" notes="Hosting Country" v-if="urlscan.page?.country" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.result-card {
  padding: 20px;

  display: flex;
  flex-direction: column;
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

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.val-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 500;
}

.value {
  font-size: 0.95rem;
  color: var(--text-main);
  font-weight: 500;
}

.highlight {
  color: var(--accent-purple);
  font-weight: 700;
  font-size: 1.1rem;
}

.text-orange {
  color: var(--accent-orange);
}
</style>
