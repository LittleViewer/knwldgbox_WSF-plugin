<script setup>
import { useI18n } from 'vue-i18n'
import { Globe, Search } from 'lucide-vue-next'

const { t } = useI18n()

defineProps({
  modelValue: { type: String, required: true },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'submit'])
</script>

<template>
  <div class="search-section glass-panel">
    <div class="search-input-wrapper">
      <Globe class="icon text-purple" size="20" />
      <input
        type="text"
        :value="modelValue"
        :placeholder="t('targetAnalysis.searchPlaceholder')"
        class="domain-input"
        @input="emit('update:modelValue', $event.target.value)"
        @keyup.enter="emit('submit')"
      />
      <button class="btn-primary scan-btn" @click="emit('submit')" :disabled="isLoading">
        <Search size="16" />
        <span v-if="isLoading">{{ t('targetAnalysis.scanning') }}</span>
        <span v-else>{{ t('targetAnalysis.analyzeTarget') }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.search-section {
  padding: 8px;

  margin-bottom: 24px;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-panel);
  padding: 8px 8px 8px 16px;

  border: 1px solid var(--border-color);
}

.domain-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-main);
  font-size: 1rem;
  outline: none;
}

.domain-input::placeholder {
  color: var(--text-muted);
}

.scan-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;

  font-weight: 600;
}

.text-purple {
  color: var(--accent-purple);
}

@media (max-width: 600px) {
  .search-input-wrapper {
    flex-direction: column;
    align-items: stretch;
    padding: 12px;
  }

  .domain-input {
    margin: 8px 0;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color);
  }

  .scan-btn {
    justify-content: center;
  }
}
</style>
