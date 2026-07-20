<script setup>
import { useI18n } from 'vue-i18n'
import { Cpu } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  technologies: { type: Array, required: true }
})
</script>

<template>
  <div class="result-card glass-panel tech-card">
    <div class="card-header">
      <Cpu size="20" class="text-purple" />
      <h3>{{ t('targetComponents.techStack.title') }}</h3>
    </div>

    <div class="card-body">
      <div v-if="!technologies || technologies.length === 0" class="empty-msg">
        {{ t('targetComponents.techStack.empty') }}
      </div>

      <div v-else class="tech-list scrollable">
        <div v-for="tech in technologies" :key="tech.name" class="tech-item data-row stack">
          <div class="tech-main">
            <span class="value">{{ tech.name }}</span>
            <span v-if="tech.versions && tech.versions.length" class="version-badge">v{{ tech.versions.join(', ') }}</span>
          </div>
          <div class="categories">
            <span v-for="cat in tech.categories" :key="cat" class="cat-tag">{{ cat }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tech-card { display: flex; flex-direction: column; }
.scrollable { max-height: 250px; overflow-y: auto; padding-right: 8px; }
.tech-list { display: flex; flex-direction: column; gap: 16px; }
.tech-item { border-bottom: 1px solid var(--overlay-5); padding-bottom: 8px; }
.tech-item:last-child { border-bottom: none; padding-bottom: 0; }
.tech-main { display: flex; align-items: center; gap: 8px; width: 100%; }
.version-badge { background: rgba(168, 85, 247, 0.2); color: #c084fc; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-family: monospace; }
.categories { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.cat-tag { font-size: 0.7rem; color: #94a3b8; background: var(--overlay-5); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--overlay-10); }
.empty-msg { font-size: 0.85rem; color: var(--text-muted); font-style: italic; }
</style>
