<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Search,
  Plus,
  Trash2,
  Copy,
  Save,
  FolderOpen,
  Zap,
  FileText,
  Mail,
  Globe,
  Lock,
  Users,
  X,
  ExternalLink,
  Code,
  MessageCircle
} from 'lucide-vue-next'

const { t } = useI18n()

const OPERATORS = [
  { value: '', label: 'Plain text', color: '#8B949E' },
  { value: 'site:', label: 'site:', color: '#FF7700' },
  { value: 'filetype:', label: 'filetype:', color: '#B026FF' },
  { value: 'intitle:', label: 'intitle:', color: '#00FF88' },
  { value: 'inurl:', label: 'inurl:', color: '#FF003C' },
  { value: 'intext:', label: 'intext:', color: '#3B82F6' },
  { value: 'ext:', label: 'ext:', color: '#B026FF' },
  { value: 'cache:', label: 'cache:', color: '#FCD34D' },
  { value: 'related:', label: 'related:', color: '#10B981' },
]

const ENGINES = [
  { id: 'google', name: 'Google', url: 'https://www.google.com/search?q=' },
  { id: 'yandex', name: 'Yandex', url: 'https://yandex.com/search/?text=' },
  { id: 'ddg', name: 'DuckDuckGo', url: 'https://duckduckgo.com/?q=' },
]

const PRESETS = computed(() => [
  { name: t('dorkBuilder.presets.findPdfs.name'), icon: FileText, desc: t('dorkBuilder.presets.findPdfs.desc'), rows: [{ operator: 'site:', value: '', exclude: false }, { operator: 'filetype:', value: 'pdf', exclude: false }] },
  { name: t('dorkBuilder.presets.emailAddresses.name'), icon: Mail, desc: t('dorkBuilder.presets.emailAddresses.desc'), rows: [{ operator: 'site:', value: '', exclude: false }, { operator: 'intext:', value: '"@gmail.com" OR "@yahoo.com"', exclude: false }] },
  { name: t('dorkBuilder.presets.loginPages.name'), icon: Lock, desc: t('dorkBuilder.presets.loginPages.desc'), rows: [{ operator: 'site:', value: '', exclude: false }, { operator: 'inurl:', value: 'login OR signin OR admin', exclude: false }] },
  { name: t('dorkBuilder.presets.openDirectories.name'), icon: FolderOpen, desc: t('dorkBuilder.presets.openDirectories.desc'), rows: [{ operator: 'intitle:', value: 'index of', exclude: false }] },
  { name: t('dorkBuilder.presets.subdomainEnum.name'), icon: Globe, desc: t('dorkBuilder.presets.subdomainEnum.desc'), rows: [{ operator: 'site:', value: '', exclude: false }, { operator: '', value: '-www', exclude: true }] },
  { name: t('dorkBuilder.presets.configFiles.name'), icon: Zap, desc: t('dorkBuilder.presets.configFiles.desc'), rows: [{ operator: 'site:', value: '', exclude: false }, { operator: 'ext:', value: 'env OR cfg OR conf OR ini', exclude: false }] },
  { name: t('dorkBuilder.presets.linkedInSearch.name'), icon: Users, desc: t('dorkBuilder.presets.linkedInSearch.desc'), rows: [{ operator: 'site:', value: 'linkedin.com', exclude: false }, { operator: '', value: '', exclude: false }] },
  { name: t('dorkBuilder.presets.telegramChannels.name'), icon: MessageCircle, desc: t('dorkBuilder.presets.telegramChannels.desc'), rows: [{ operator: 'site:', value: 't.me', exclude: false }, { operator: 'intext:', value: 'subscribers', exclude: false }] },
  { name: t('dorkBuilder.presets.telegramMessages.name'), icon: MessageCircle, desc: t('dorkBuilder.presets.telegramMessages.desc'), rows: [{ operator: 'site:', value: 't.me/s/', exclude: false }, { operator: '', value: '', exclude: false }] },
])

const STORAGE_KEY = 'knwldg_saved_dorks'
const rows = ref([{ id: Date.now(), operator: '', value: '', exclude: false }])
const savedDorks = ref([])
const copyFeedback = ref(false)
const activePreset = ref(null)
const selectedEngine = ref('google')

const showSaveModal = ref(false)
const dorkNameToSave = ref('')

onMounted(() => {
  try {
    savedDorks.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    savedDorks.value = []
  }
})

function addRow() {
  rows.value.push({ id: Date.now(), operator: '', value: '', exclude: false })
}

function removeRow(id) {
  rows.value = rows.value.filter(r => r.id !== id)
  if (rows.value.length === 0) addRow()
}

function applyPreset(preset) {
  activePreset.value = preset.name
  rows.value = preset.rows.map((r, i) => ({
    id: Date.now() + i,
    operator: r.operator,
    value: r.value,
    exclude: r.exclude,
  }))
  setTimeout(() => { activePreset.value = null }, 1500)
}

function getOperatorColor(opValue) {
  const op = OPERATORS.find(o => o.value === opValue)
  return op ? op.color : '#8B949E'
}

const query = computed(() => {
  const parts = rows.value
    .filter(r => r.value.trim() || r.operator)
    .map(r => {
      const term = r.value.trim()
      if (!term && !r.operator) return ''
      const prefix = r.exclude ? '-' : ''
      // If there's an operator and a term with spaces, quote it. If it's plain text, leave as is.
      if (r.operator) {
        const safeTerm = term.includes(' ') && !term.startsWith('"') ? `"${term}"` : term
        return `${prefix}${r.operator}${safeTerm}`
      }
      return `${prefix}${term}`
    })
    .filter(Boolean)
  return parts.join(' ')
})

const searchUrl = computed(() => {
  if (!query.value.trim()) return ''
  const engine = ENGINES.find(e => e.id === selectedEngine.value)
  return `${engine.url}${encodeURIComponent(query.value)}`
})

function runSearch() {
  if (searchUrl.value) window.open(searchUrl.value, '_blank', 'noopener,noreferrer')
}

async function copyQuery() {
  if (!query.value.trim()) return
  try {
    await navigator.clipboard.writeText(query.value)
    copyFeedback.value = true
    setTimeout(() => { copyFeedback.value = false }, 1500)
  } catch {
    // fallback
  }
}

function triggerSave() {
  if (!query.value.trim()) return
  dorkNameToSave.value = ''
  showSaveModal.value = true
}

function confirmSaveDork() {
  if (!query.value.trim() || !dorkNameToSave.value.trim()) return
  savedDorks.value.unshift({
    id: Date.now(),
    name: dorkNameToSave.value.trim(),
    query: query.value,
    rows: rows.value.map(r => ({ ...r })),
    savedAt: new Date().toISOString(),
  })
  localStorage.setItem(STORAGE_KEY, JSON.stringify(savedDorks.value))
  showSaveModal.value = false
}

function loadDork(dork) {
  rows.value = dork.rows.map(r => ({ ...r, id: Date.now() + Math.random() }))
}

function deleteDork(id) {
  savedDorks.value = savedDorks.value.filter(d => d.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(savedDorks.value))
}
</script>

<template>
  <div class="dork-page">
    <div class="header-section">
      <h1 class="page-title">{{ t('dorkBuilder.title') }}</h1>
      <p class="page-subtitle">{{ t('dorkBuilder.subtitle') }}</p>
    </div>

    <!-- Save Dork Modal -->
    <div class="save-overlay" v-if="showSaveModal">
      <div class="save-modal glass-panel">
        <h3>{{ t('dorkBuilder.namePrompt') }}</h3>
        <p>{{ t('dorkBuilder.saveModalText') }}</p>
        <div class="form-group">
          <input type="text" v-model="dorkNameToSave" :placeholder="t('dorkBuilder.namePlaceholder')" class="name-input mono" @keyup.enter="confirmSaveDork" autofocus />
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showSaveModal = false">{{ t('common.cancel') }}</button>
          <button class="btn-primary" @click="confirmSaveDork" :disabled="!dorkNameToSave.trim()">
            <Save size="16" /> {{ t('dorkBuilder.save') }}
          </button>
        </div>
      </div>
    </div>

    <div class="layout-grid">

      <!-- Main Builder Column -->
      <div class="builder-column">
        <div class="panel glass-panel builder-panel">
          <div class="panel-header">
            <div class="title-with-icon">
              <Code class="text-orange" />
              <h2>{{ t('dorkBuilder.builderTitle') }}</h2>
            </div>
          </div>

          <div class="rows-container">
            <div
              v-for="(row, index) in rows"
              :key="row.id"
              class="dork-row"
              :class="{ 'is-excluded': row.exclude }"
            >
              <div class="row-drag-handle">{{ index + 1 }}</div>

              <div class="operator-wrapper" :style="{ '--op-color': getOperatorColor(row.operator) }">
                <select v-model="row.operator" class="operator-select">
                  <option v-for="op in OPERATORS" :key="op.value" :value="op.value">
                    {{ op.value ? op.label : t('dorkBuilder.plainText') }}
                  </option>
                </select>
              </div>

              <input
                v-model="row.value"
                type="text"
                class="value-input mono"
                :placeholder="t('dorkBuilder.searchTermPlaceholder')"
              />

              <div class="row-actions">
                <label class="exclude-toggle" :title="t('dorkBuilder.exclude')">
                  <input type="checkbox" v-model="row.exclude" />
                  <div class="exclude-btn">
                    <span>{{ t('dorkBuilder.exclude') }}</span>
                  </div>
                </label>

                <button class="btn-icon-only remove" @click="removeRow(row.id)" :title="t('dorkBuilder.remove')">
                  <Trash2 size="16" />
                </button>
              </div>
            </div>

            <button class="btn-add-row" @click="addRow">
              <Plus size="16" /> {{ t('dorkBuilder.addCondition') }}
            </button>
          </div>

          <!-- Live Preview -->
          <div class="preview-section">
            <div class="preview-header">
              <span>{{ t('dorkBuilder.previewLabel') }}</span>
            </div>
            <div class="preview-box mono" :class="{ 'is-empty': !query.trim() }">
              {{ query || t('dorkBuilder.previewEmpty') }}
            </div>
          </div>

          <!-- Actions -->
          <div class="builder-actions">
            <div class="engine-selector">
              <select v-model="selectedEngine">
                <option v-for="engine in ENGINES" :key="engine.id" :value="engine.id">{{ engine.name }}</option>
              </select>
            </div>

            <div class="action-buttons-group">
              <button class="btn-secondary" :disabled="!query.trim()" @click="copyQuery">
                <Copy size="16" /> {{ copyFeedback ? t('dorkBuilder.copied') : t('dorkBuilder.copy') }}
              </button>
              <button class="btn-secondary" :disabled="!query.trim()" @click="triggerSave">
                <Save size="16" /> {{ t('dorkBuilder.save') }}
              </button>
              <button class="btn-primary" :disabled="!query.trim()" @click="runSearch">
                <Search size="16" /> {{ t('dorkBuilder.search') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Saved Dorks -->
        <div class="panel glass-panel" v-if="savedDorks.length > 0">
          <div class="panel-header">
            <h2>{{ t('dorkBuilder.savedDorks') }}</h2>
          </div>
          <div class="saved-grid">
            <div v-for="dork in savedDorks" :key="dork.id" class="saved-card">
              <div class="saved-content" @click="loadDork(dork)">
                <h4>{{ dork.name }}</h4>
                <div class="saved-query mono">{{ dork.query }}</div>
              </div>
              <button class="btn-icon-only remove" @click="deleteDork(dork.id)" title="Supprimer">
                <X size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Presets Column -->
      <div class="presets-column">
        <div class="panel glass-panel presets-panel">
          <div class="panel-header">
            <h2>{{ t('dorkBuilder.quickTemplates') }}</h2>
          </div>
          <div class="presets-list">
            <div
              v-for="preset in PRESETS"
              :key="preset.name"
              class="preset-item"
              :class="{ active: activePreset === preset.name }"
              @click="applyPreset(preset)"
            >
              <div class="preset-icon-wrapper">
                <component :is="preset.icon" size="20" />
              </div>
              <div class="preset-details">
                <span class="preset-name">{{ preset.name }}</span>
                <span class="preset-desc">{{ preset.desc }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.dork-page {
  flex: 1;
  overflow-y: auto;
  padding-right: 16px;
}

.header-section { margin-bottom: 32px; }
.page-title { font-size: 2.2rem; margin-bottom: 8px; color: var(--text-main); }
.page-subtitle { color: var(--text-muted); font-size: 1rem; }

/* ── Modal ───────────────────────────── */
.save-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: var(--bg-panel);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-modal {
  width: 400px;
  max-width: 90%;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.save-modal h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.2rem;
}

.save-modal p {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 0;
}

.name-input {
  width: 100%;
  background: var(--overlay-10);
  border: 1px solid var(--border-color);
  padding: 10px 12px;
  color: var(--text-main);
  outline: none;
  transition: var(--transition-base);
}

.name-input:focus {
  border-color: var(--accent-orange);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.btn-cancel {
  background: transparent;
  color: var(--text-muted);
  border: none;
  cursor: pointer;
  padding: 8px 16px;
  font-weight: 600;
}

.btn-cancel:hover {
  color: var(--text-main);
}

.text-orange { color: var(--accent-orange); }

.layout-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  align-items: start;
}

.panel {
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
}

.panel-header {
  margin-bottom: 20px;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 12px;
}

.panel-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-main);
  margin: 0;
}

/* ── Builder Rows ───────────────────────────── */
.rows-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.dork-row {
  display: flex;
  align-items: stretch;
  gap: 12px;
  padding: 12px;
  background: var(--overlay-8);
  border: 1px solid var(--border-color);

  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.dork-row:focus-within {
  border-color: rgba(var(--accent-rgb), 0.4);

  transform: translateY(-2px);
  background: var(--overlay-10);
}

.dork-row.is-excluded {
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.05);
}
.dork-row.is-excluded::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--accent-red);
}

.row-drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  color: var(--text-muted);
  font-weight: 700;
  font-size: 0.9rem;
  opacity: 0.5;
}

.operator-wrapper {
  position: relative;

  background: rgba(var(--op-color), 0.1); /* Fallback */
  border: 1px solid var(--op-color);
  display: flex;
  align-items: stretch;
}
.operator-wrapper::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0; right: 0;
  background: var(--op-color);
  opacity: 0.15;

  pointer-events: none;
}

.operator-select {
  background: transparent;
  border: none;
  color: var(--op-color);
  font-weight: 700;
  padding: 0 16px;
  font-size: 0.9rem;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
  outline: none;
  min-width: 130px;
  appearance: none;
}
.operator-select option {
  background: var(--bg-panel);
  color: var(--text-main);
}

.value-input {
  flex: 1;
  background: var(--overlay-8);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 0 16px;

  font-size: 0.95rem;
  outline: none;
  transition: var(--transition);
}
.value-input:focus {
  border-color: var(--accent-orange);
  background: var(--overlay-8);
}
.value-input::placeholder {
  color: var(--text-muted);
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.exclude-toggle input { display: none; }
.exclude-btn {
  background: var(--overlay-10);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 8px 12px;

  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 100%;
  display: flex;
  align-items: center;
}
.exclude-toggle input:checked + .exclude-btn {
  background: var(--overlay-10);
  border-color: var(--accent-red);
  color: var(--accent-red);
}

.btn-icon-only {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;

  transition: all 0.2s ease;
}
.btn-icon-only:hover {
  background: var(--overlay-10);
  color: var(--text-main);
}
.btn-icon-only.remove:hover {
  background: var(--overlay-10);
  color: var(--accent-red);
}

.btn-add-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: var(--overlay-8);
  border: 1px dashed var(--border-color);
  color: var(--text-muted);
  padding: 12px;

  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-add-row:hover {
  background: var(--overlay-10);
  border-color: var(--accent-orange);
  color: var(--text-main);
}

/* ── Live Preview ───────────────────────────── */
.preview-section {
  background: var(--bg-dark);

  border: 1px solid rgba(var(--accent-rgb), 0.2);
  margin-bottom: 24px;
  overflow: hidden;

}

.preview-header {
  background: rgba(var(--accent-rgb), 0.1);
  padding: 8px 16px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-orange);
  letter-spacing: 0.1em;
  border-bottom: 1px solid rgba(var(--accent-rgb), 0.2);
}

.preview-box {
  padding: 20px 16px;
  font-size: 1.1rem;
  color: var(--text-main);
  word-break: break-all;
  line-height: 1.5;
}
.preview-box.is-empty {
  color: var(--text-muted);
}

/* ── Actions ───────────────────────────── */
.builder-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

.engine-selector select {
  background: var(--overlay-10);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 10px 16px;

  font-size: 0.95rem;
  outline: none;
  cursor: pointer;
}
.engine-selector select:focus {
  border-color: var(--accent-orange);
}

.action-buttons-group {
  display: flex;
  gap: 12px;
}

.btn-secondary, .btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;

  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-secondary {
  background: var(--overlay-10);
  color: var(--text-main);
  border: 1px solid var(--border-color);
}
.btn-secondary:hover:not(:disabled) {
  background: var(--overlay-10);
  border-color: var(--border-color);
}

.btn-primary {
  background: var(--accent-orange);
  color: var(--text-main);

}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);

}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Saved Dorks ───────────────────────────── */
.saved-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.saved-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--overlay-8);
  border: 1px solid var(--border-color);

  transition: all 0.2s ease;
}
.saved-card:hover {
  background: var(--overlay-8);
  border-color: rgba(var(--accent-rgb), 0.3);
}

.saved-content {
  flex: 1;
  cursor: pointer;
  overflow: hidden;
}

.saved-content h4 {
  margin: 0 0 4px 0;
  color: var(--text-main);
  font-size: 0.95rem;
}

.saved-query {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Presets Column ───────────────────────────── */
.presets-panel {
  position: sticky;
  top: 16px;
}

.presets-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preset-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--overlay-8);
  border: 1px solid var(--border-color);

  cursor: pointer;
  transition: all 0.2s ease;
}

.preset-item:hover {
  background: var(--overlay-10);
  border-color: var(--border-color);
  transform: translateX(4px);
}

.preset-item.active {
  background: rgba(var(--accent-rgb), 0.1);
  border-color: rgba(var(--accent-rgb), 0.3);
}

.preset-icon-wrapper {
  width: 40px;
  height: 40px;

  background: var(--overlay-10);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-orange);
  flex-shrink: 0;
}
.preset-item:hover .preset-icon-wrapper {
  background: rgba(var(--accent-rgb), 0.2);
}

.preset-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.preset-name {
  color: var(--text-main);
  font-weight: 600;
  font-size: 0.95rem;
}

.preset-desc {
  color: var(--text-muted);
  font-size: 0.75rem;
  line-height: 1.3;
}

@media (max-width: 1024px) {
  .layout-grid {
    grid-template-columns: 1fr;
  }
  .presets-panel {
    position: static;
  }
}

@media (max-width: 768px) {
  .dork-row {
    flex-wrap: wrap;
  }
  .value-input {
    width: 100%;
    order: 3;
    margin-top: 8px;
    padding: 12px;
  }
  .builder-actions {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  .action-buttons-group {
    flex-wrap: wrap;
  }
  .btn-secondary, .btn-primary {
    flex: 1;
    justify-content: center;
  }
}
</style>
