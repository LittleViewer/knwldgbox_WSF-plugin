<script setup>
import { useI18n } from 'vue-i18n'
import { FileText, Play } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  crawl: { type: Object, required: true },
  domain: { type: String, required: true }
})
</script>

<template>
  <div class="result-card glass-panel pages-card">
    <div class="card-header">
      <FileText size="20" class="text-green" />
      <h3>{{ t('targetComponents.pages.title') }}</h3>
    </div>

    <div class="card-body scrollable">
      <div v-if="crawl.internal_links.length === 0" class="empty-msg">
        {{ t('targetComponents.pages.empty') }}
      </div>

      <div v-else class="pages-list">
        <div v-for="link in crawl.internal_links" :key="link" class="page-item">
          <Play size="12" class="text-green arrow-icon" />
          <a :href="`https://${domain}${link.startsWith('/') ? '' : '/'}${link}`" target="_blank" rel="noopener noreferrer" class="path mono truncate" :title="link">{{ link }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pages-card {
  display: flex;
  flex-direction: column;
}

.scrollable {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.pages-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.arrow-icon {
  flex-shrink: 0;
}

.path {
  color: var(--text-main);
  font-size: 0.85rem;
  text-decoration: none;
  transition: color 0.2s;
}

.path:hover {
  color: var(--accent-green);
  text-decoration: underline;
}

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.empty-msg {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}
</style>
