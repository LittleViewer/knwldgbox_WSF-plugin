<script setup>
import { Link, Play } from 'lucide-vue-next'

const props = defineProps({
  crawl: { type: Object, required: true },
  domain: { type: String, required: true }
})
</script>

<template>
  <div class="result-card glass-panel linked-pages-card">
    <div class="card-header">
      <Link size="20" class="text-green" />
      <h3>Linked Pages</h3>
    </div>
    
    <div class="card-body">
      <span class="section-title">Summary</span>
      
      <div class="data-row">
        <span class="label">Internal Link Count</span>
        <span class="value mono">{{ crawl.internal_count }}</span>
      </div>
      
      <div class="data-row" style="margin-bottom: 12px;">
        <span class="label">External Link Count</span>
        <span class="value mono">{{ crawl.external_count }}</span>
      </div>

      <details class="link-details">
        <summary><Play size="12" class="arrow" /> Internal Links</summary>
        <div class="details-content scrollable">
          <a v-for="link in crawl.internal_links" :key="link" :href="`https://${domain}${link.startsWith('/') ? '' : '/'}${link}`" target="_blank" rel="noopener noreferrer" class="path mono" :title="link">{{ link }}</a>
        </div>
      </details>

      <details class="link-details">
        <summary><Play size="12" class="arrow" /> External Links</summary>
        <div class="details-content scrollable">
          <a v-for="link in crawl.external_links" :key="link" :href="link" target="_blank" rel="noopener noreferrer" class="path mono" :title="link">{{ link }}</a>
        </div>
      </details>
    </div>
  </div>
</template>

<style scoped>
.linked-pages-card {
  display: flex;
  flex-direction: column;
}

.section-title {
  color: var(--accent-green);
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.link-details {
  margin-top: 8px;
}

.link-details summary {
  cursor: pointer;
  color: var(--accent-green);
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
  list-style: none; /* remove default arrow */
  user-select: none;
}

.link-details summary::-webkit-details-marker {
  display: none;
}

.link-details[open] .arrow {
  transform: rotate(90deg);
}

.arrow {
  transition: transform 0.2s;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
  margin-left: 20px;
  border-left: 1px solid var(--overlay-10);
  padding-left: 12px;
  padding-bottom: 20px;
}

.scrollable {
  max-height: 250px;
  overflow-y: auto;
}

.path {
  color: var(--text-main);
  font-size: 0.85rem;
  line-height: 1.5;
  text-decoration: none;
  transition: color 0.2s;
  display: block;
  padding: 4px 0;
  word-break: break-all;
}

.path:hover {
  color: var(--accent-green);
  text-decoration: underline;
}
</style>
