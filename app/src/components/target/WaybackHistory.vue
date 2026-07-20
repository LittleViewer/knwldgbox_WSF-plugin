<script setup>
import { useI18n } from 'vue-i18n'
import { History, ExternalLink } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  wayback: { type: Object, required: true }
})

const formatTimestamp = (ts) => {
  if (!ts || ts.length < 8) return t('targetComponents.waybackHistory.unknown')
  const year = ts.substring(0, 4)
  const month = ts.substring(4, 6)
  const day = ts.substring(6, 8)
  return `${year}-${month}-${day}`
}
</script>

<template>
  <div class="result-card glass-panel wayback-card">
    <div class="card-header">
      <History size="20" class="text-orange" />
      <h3>{{ t('targetComponents.waybackHistory.title') }}</h3>
    </div>

    <div class="card-body">
      <div v-if="!wayback.first_snapshot" class="empty-msg">
        {{ t('targetComponents.waybackHistory.empty') }}
      </div>

      <template v-else>
        <div class="data-row">
          <span class="label">{{ t('targetComponents.waybackHistory.firstSnapshot') }}</span>
          <span class="value mono">{{ formatTimestamp(wayback.first_snapshot) }}</span>
        </div>

        <div class="data-row">
          <span class="label">{{ t('targetComponents.waybackHistory.lastSnapshot') }}</span>
          <span class="value mono">{{ formatTimestamp(wayback.last_snapshot) }}</span>
        </div>

        <a :href="wayback.archive_url" target="_blank" rel="noopener noreferrer" class="archive-btn mt-2">
          <span>{{ t('targetComponents.waybackHistory.viewAll') }}</span>
          <ExternalLink size="14" />
        </a>
      </template>
    </div>
  </div>
</template>

<style scoped>
.wayback-card { display: flex; flex-direction: column; }
.mt-2 { margin-top: 12px; }
.archive-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
  color: #fb923c;
  padding: 8px 12px;

  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}
.archive-btn:hover { background: rgba(249, 115, 22, 0.2); }
.empty-msg { font-size: 0.85rem; color: var(--text-muted); font-style: italic; }
</style>
