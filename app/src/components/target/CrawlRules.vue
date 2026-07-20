<script setup>
import { useI18n } from 'vue-i18n'
import { Bot } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  rules: { type: Array, required: true }
})
</script>

<template>
  <div class="result-card glass-panel crawl-card">
    <div class="card-header">
      <Bot size="20" class="text-green" />
      <h3>{{ t('targetComponents.crawlRules.title') }}</h3>
    </div>

    <div class="card-body">
      <div v-if="rules.length === 0" class="empty-msg">
        {{ t('targetComponents.crawlRules.empty') }}
      </div>

      <div v-else class="rules-list scrollable">
        <div v-for="(rule, index) in rules" :key="index" class="data-row stack">
          <div class="rule-header">
            <span class="label">{{ t('targetComponents.crawlRules.userAgent') }}</span>
            <span class="value mono">{{ rule.agent }}</span>
          </div>
          <div class="rule-path">
            <span :class="['rule-type', rule.rule === 'Allow' ? 'text-green' : 'text-red']">
              {{ rule.rule }}
            </span>
            <span class="path mono truncate" :title="rule.path">{{ rule.path }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.crawl-card {
  display: flex;
  flex-direction: column;
}

.scrollable {
  max-height: 250px;
  overflow-y: auto;
  padding-right: 8px;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.rule-path {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
}

.rule-type {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
}

.path {
  color: var(--text-main);
  font-size: 0.85rem;
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
