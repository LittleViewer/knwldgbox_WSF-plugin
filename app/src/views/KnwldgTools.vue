<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Image as ImageIcon, ImageOff } from 'lucide-vue-next'
import CollageModule from '../components/tools/CollageModule.vue'
import CrossModule from '../components/tools/CrossModule.vue'

const activeTab = ref('collage')
const { t } = useI18n()
</script>

<template>
  <div class="knwldg-tools-page">
    <div class="header-section">
      <h1 class="page-title">{{ t('knwldgTools.title') }}</h1>
      <p class="page-subtitle">{{ t('knwldgTools.subtitle') }}</p>
    </div>

    <!-- Tabs Navigation -->
    <div class="tabs-container">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'collage' }"
        @click="activeTab = 'collage'"
      >
          <ImageIcon size="18" /> {{ t('knwldgTools.collageMaker') }}
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'cross' }"
        @click="activeTab = 'cross'"
      >
          <ImageOff size="18" /> {{ t('knwldgTools.crossCreator') }}
      </button>
      <!-- Add more tabs here in the future -->
    </div>

    <!-- Tab Content -->
    <div v-show="activeTab === 'collage'" class="tab-content">
      <CollageModule />
    </div>

    <div v-show="activeTab === 'cross'" class="tab-content">
      <CrossModule />
    </div>
  </div>
</template>

<style scoped>
.knwldg-tools-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-right: 8px;
}

.header-section { margin-bottom: 16px; }
.page-title { font-size: 2rem; margin-bottom: 8px; }
.page-subtitle { color: var(--text-muted); font-size: 0.95rem; }

.tabs-container {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;

  font-weight: 500;
  color: var(--text-muted);
  background: transparent;
  transition: var(--transition);
}

.tab-btn:hover {
  background: var(--overlay-8);
  color: var(--text-main);
}

.tab-btn.active {
  background: rgba(var(--accent-rgb), 0.1);
  color: var(--accent-orange);
  border: 1px solid rgba(var(--accent-rgb), 0.3);
}

.tab-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}
</style>
