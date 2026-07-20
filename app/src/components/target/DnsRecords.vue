<script setup>
import { useI18n } from 'vue-i18n'
import { Network } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  dns: { type: Object, required: true }
})
</script>

<template>
  <div class="result-card glass-panel dns-card">
    <div class="card-header">
      <Network size="20" class="text-blue" />
      <h3>{{ t('targetComponents.dnsRecords.title') }}</h3>
    </div>

    <div class="card-body scrollable">
      <div v-for="(records, type) in dns" :key="type" class="dns-section">
        <div class="dns-type" v-if="records.length > 0">
          <span class="type-badge">{{ type }}</span>
          <div class="records-list">
            <div v-for="record in records" :key="record" class="data-row">
              <span class="value mono">{{ record }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="Object.values(dns).every(arr => arr.length === 0)" class="empty-msg">
        {{ t('targetComponents.dnsRecords.empty') }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.dns-card {
  display: flex;
  flex-direction: column;
}

.scrollable {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 8px;
}

.dns-section {
  margin-bottom: 12px;
}

.dns-type {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.type-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-orange);
  background: rgba(var(--accent-rgb), 0.1);
  padding: 2px 6px;

  width: fit-content;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 8px;
  border-left: 2px solid var(--overlay-10);
}

.value.mono {
  font-size: 0.85rem;
  color: var(--text-main);
  word-break: break-all;
}

.empty-msg {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}
</style>
