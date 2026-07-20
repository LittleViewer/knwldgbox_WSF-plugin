<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ShieldAlert, Search, ShieldCheck, Mail, X, Loader2 } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  config: { type: Object, required: true }
})



const email = ref('')
const isSearching = ref(false)
const hasSearched = ref(false)
const breaches = ref([])
const errorMsg = ref('')

async function checkEmail() {
  if (!email.value || !email.value.includes('@')) return

  isSearching.value = true
  hasSearched.value = false
  errorMsg.value = ''
  breaches.value = []

  try {
    const res = await fetch(`https://api.xposedornot.com/v1/check-email/${encodeURIComponent(email.value)}`)

    if (res.status === 404) {
      // 404 means no breaches found on XposedOrNot
      hasSearched.value = true
      return
    }

    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`)
    }

    const data = await res.json()
    if (data.breaches && data.breaches.length > 0) {
      breaches.value = data.breaches[0]
    }

    hasSearched.value = true
  } catch (err) {
    errorMsg.value = t('pwnedChecker.error')
  } finally {
    isSearching.value = false
  }
}


</script>

<template>
  <div class="monitor-block pwned-block" :style="{ height: config.height ? `${config.height}px` : '350px' }">
    <div class="block-header glass-panel">
      <div class="header-left">
        <div class="icon-box" style="background: rgba(var(--accent-rgb), 0.1); color: var(--accent-orange);">
          <ShieldAlert size="16" />
        </div>
        <h3 class="block-title">{{ t('pwnedChecker.title') }}</h3>
      </div>
    </div>

    <div class="block-content custom-scrollbar">
      <div class="search-section">
        <p class="desc">{{ t('pwnedChecker.desc') }}</p>

        <form @submit.prevent="checkEmail" class="search-form">
          <div class="input-wrapper">
            <Mail size="16" class="input-icon" />
            <input
              type="email"
              v-model="email"
              :placeholder="t('pwnedChecker.emailPlaceholder')"
              required
              class="email-input"
            />
          </div>
          <button type="submit" class="search-btn" :disabled="isSearching || !email">
            <Loader2 v-if="isSearching" size="16" class="spin" />
            <Search v-else size="16" />
            {{ t('pwnedChecker.check') }}
          </button>
        </form>
      </div>

      <div class="results-section" v-if="hasSearched || errorMsg">
        <div v-if="errorMsg" class="alert alert-error">
          {{ errorMsg }}
        </div>

        <div v-else-if="breaches.length === 0" class="alert alert-success">
          <ShieldCheck size="32" class="mb-2" />
          <h4 class="m-0">{{ t('pwnedChecker.goodNews') }}</h4>
          <p class="m-0 text-sm">{{ t('pwnedChecker.noBreaches') }}</p>
        </div>

        <div v-else class="breach-results">
          <div class="alert alert-warning">
            <ShieldAlert size="24" class="mb-2" />
            <h4 class="m-0 text-lg">{{ t('pwnedChecker.compromised') }}</h4>
            <p class="m-0 text-sm">{{ t('pwnedChecker.foundInBreaches', { count: breaches.length }) }}</p>
          </div>

          <div class="breach-tags">
            <span class="breach-tag" v-for="breach in breaches" :key="breach">
              {{ breach }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.monitor-block {
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);

  overflow: hidden;
  resize: vertical;
  min-height: 250px;
  position: relative;
  transition: border-color 0.2s ease;
}

.monitor-block:focus-within {
  border-color: rgba(var(--accent-rgb), 0.4);
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  background: rgba(20, 20, 25, 0.8);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-box {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;

}

.block-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-main);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition);
  padding: 4px;

}

.icon-btn:hover {
  color: var(--text-main);
  background: var(--overlay-10);
}
.close-btn:hover {
  color: var(--accent-red);
  background: rgba(239, 68, 68, 0.1);
}

.block-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

.search-form {
  display: flex;
  gap: 12px;
}

.input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
}

.email-input {
  width: 100%;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 10px 12px 10px 36px;

  font-size: 0.9rem;
  outline: none;
  transition: var(--transition);
}

.email-input:focus {
  border-color: var(--accent-orange);
  background: var(--bg-panel);
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--accent-orange);
  color: #000;
  border: none;
  padding: 0 16px;

  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
}
.search-btn:hover:not(:disabled) {
  background: #fbbf24;
}
.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin { 100% { transform: rotate(360deg); } }

.alert {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px;

}

.alert-success {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: var(--accent-green);
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--accent-red);
}

.alert-warning {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--accent-red);
  margin-bottom: 16px;
}

.mb-2 { margin-bottom: 8px; }
.m-0 { margin: 0; }
.text-sm { font-size: 0.85rem; }
.text-lg { font-size: 1.2rem; }

.breach-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.breach-tag {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #FCA5A5;
  padding: 4px 10px;

  font-size: 0.8rem;
  font-weight: 500;
}
</style>
