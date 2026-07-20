<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { Shield } from 'lucide-vue-next'

defineProps({
  verdicts: { type: Object, required: true }
})

function verdictLabel(verdict) {
  return verdict?.malicious ? 'Malicious' : 'Clean'
}

function verdictClass(verdict) {
  return verdict?.malicious ? 'text-red' : 'text-green'
}
</script>

<template>
  <div class="result-card glass-panel">
    <div class="card-header">
      <Shield size="18" class="text-red" />
      <h3>{{ t('targetAnalysis.components.verdicts.title') }}</h3>
    </div>
    <div class="card-body">
      <div class="verdicts-grid">
        <div class="verdict-box" v-if="verdicts.overall">
          <span class="v-label">{{ t('targetAnalysis.components.verdicts.overall') }}</span>
          <span class="v-score" :class="verdictClass(verdicts.overall)">
            {{ verdictLabel(verdicts.overall) }}
          </span>
          <span class="v-sub">Score: {{ verdicts.overall.score }}</span>
        </div>
        <div class="verdict-box" v-if="verdicts.urlscan">
          <span class="v-label">{{ t('targetAnalysis.components.verdicts.urlscan') }}</span>
          <span class="v-score" :class="verdictClass(verdicts.urlscan)">
            {{ verdictLabel(verdicts.urlscan) }}
          </span>
          <span class="v-sub">Score: {{ verdicts.urlscan.score }}</span>
        </div>
        <div class="verdict-box" v-if="verdicts.engines">
          <span class="v-label">{{ t('targetAnalysis.components.verdicts.engines') }}</span>
          <span class="v-score" :class="verdictClass(verdicts.engines)">
            {{ verdictLabel(verdicts.engines) }}
          </span>
          <span class="v-sub">Score: {{ verdicts.engines.score }}</span>
        </div>
        <div class="verdict-box" v-if="verdicts.community">
          <span class="v-label">{{ t('targetAnalysis.components.verdicts.community') }}</span>
          <span class="v-score" :class="verdicts.community.score < 0 ? 'text-red' : 'text-green'">
            {{ verdicts.community.score < 0 ? 'Malicious' : 'Clean' }}
          </span>
          <span class="v-sub">Score: {{ verdicts.community.score }}</span>
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

.verdicts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.verdict-box {
  background: var(--overlay-8);
  border: 1px solid var(--border-color);
  padding: 12px;

  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.v-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.v-score {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.v-sub {
  font-size: 0.8rem;
  color: var(--text-main);
  opacity: 0.7;
}

.text-red { color: var(--accent-red); }
.text-green { color: var(--accent-green); }
</style>
