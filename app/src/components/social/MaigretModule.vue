<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Search, Loader2, ExternalLink, User, Globe2, Clock, Settings, ChevronDown, ChevronUp } from 'lucide-vue-next'
import { apiService } from '../../services/api'

const { t } = useI18n()

const username = ref('')
const isSearching = ref(false)
const progressPercent = ref(0)
const progressText = ref('')
const results = ref([])
const expandedCards = ref(new Set())
const ws = ref(null)

const showSettings = ref(false)
const allSites = ref(false)
const timeout = ref(10)

const sortedResults = computed(() => {
  return [...results.value].sort((a, b) => {
    const aCount = Object.keys(a.tags).length
    const bCount = Object.keys(b.tags).length
    return bCount - aCount
  })
})

const richResults = computed(() => sortedResults.value.filter(r => Object.keys(r.tags).length > 0))
const basicResults = computed(() => sortedResults.value.filter(r => Object.keys(r.tags).length === 0))

function toggleExpand(site) {
  if (expandedCards.value.has(site)) {
    expandedCards.value.delete(site)
  } else {
    expandedCards.value.add(site)
  }
}

function startSearch() {
  if (!username.value.trim() || isSearching.value) return

  results.value = []
  expandedCards.value = new Set()
  progressPercent.value = 0
  isSearching.value = true
  progressText.value = t('socialForensics.maigret.initializing')

  ws.value = apiService.createMaigretWebSocket()

  ws.value.onopen = () => {
    ws.value.send(JSON.stringify({
      action: 'search',
      username: username.value,
      allSites: allSites.value,
      timeout: timeout.value
    }))
    progressText.value = t('socialForensics.maigret.gathering', { username: `@${username.value}` })
  }

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'found') {
      results.value.push({
        site: data.site,
        url: data.url,
        tags: {}
      })
    } else if (data.type === 'tag') {
      const entry = results.value.find(r => r.site === data.site)
      if (entry) {
        entry.tags[data.key] = data.value
      }
    } else if (data.type === 'enrich') {
      const entry = results.value.find(r => r.site === data.site)
      if (entry && data.ids) {
        for (const [key, val] of Object.entries(data.ids)) {
          if (val && !key.startsWith('_')) {
            entry.tags[key] = String(val)
          }
        }
      }
    } else if (data.type === 'progress') {
      progressPercent.value = data.percent
      progressText.value = t('socialForensics.maigret.progress', { percent: data.percent })
    } else if (data.type === 'info') {
      progressText.value = data.text
    } else if (data.type === 'done') {
      isSearching.value = false
      progressPercent.value = 100
      progressText.value = t('socialForensics.maigret.complete', { count: results.value.length })
      if (ws.value) ws.value.close()
    } else if (data.type === 'error') {
      isSearching.value = false
      progressText.value = `${t('socialForensics.maigret.errorPrefix')} ${data.text}`
      if (ws.value) ws.value.close()
    }
  }

  ws.value.onerror = () => {
    isSearching.value = false
    progressText.value = t('socialForensics.maigret.wsError')
  }
}

function stopSearch() {
  if (ws.value && isSearching.value) {
    ws.value.close()
    isSearching.value = false
    progressText.value = t('socialForensics.maigret.aborted')
  }
}

function getDomain(url) {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url
  }
}

function getFaviconUrl(url) {
  try {
    const domain = new URL(url).hostname
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
  } catch {
    return ''
  }
}

function getHighlightTags(tags) {
  const priority = ['fullname', 'username', 'uid', 'bio', 'follower_count', 'created_at', 'country', 'location', 'gender', 'is_verified']
  const highlights = {}
  for (const key of priority) {
    if (tags[key] !== undefined) {
      highlights[key] = tags[key]
    }
  }
  return highlights
}

function getExtraTags(tags) {
  const priority = new Set(['fullname', 'username', 'uid', 'bio', 'follower_count', 'created_at', 'country', 'location', 'gender', 'is_verified'])
  const extra = {}
  for (const [key, val] of Object.entries(tags)) {
    if (!priority.has(key)) {
      extra[key] = val
    }
  }
  return extra
}

function formatTagLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

onUnmounted(() => {
  stopSearch()
})
</script>

<template>
  <div class="maigret-module">
    <div class="search-panel glass-panel">
      <div class="input-wrapper">
        <User class="icon-user" size="20" />
        <input
          v-model="username"
          type="text"
          :placeholder="t('socialForensics.maigret.placeholder')"
          @keyup.enter="startSearch"
          :disabled="isSearching"
        />
        <button class="btn-settings" @click="showSettings = !showSettings" :class="{ active: showSettings }">
          <Settings size="18" />
        </button>
        <button class="btn-search" @click="startSearch" v-if="!isSearching">
          <Search size="18" /> {{ t('socialForensics.maigret.search') }}
        </button>
        <button class="btn-stop" @click="stopSearch" v-else>
          <Loader2 size="18" class="spin" /> {{ t('socialForensics.maigret.abort') }}
        </button>
      </div>
      <div class="settings-panel" v-if="showSettings">
        <div class="setting-item">
          <div class="setting-header">
            <Globe2 size="16" class="text-orange" />
            <label>{{ t('socialForensics.maigret.allSites') }}</label>
            <label class="switch">
              <input type="checkbox" v-model="allSites" :disabled="isSearching">
              <span class="slider round"></span>
            </label>
          </div>
          <p class="setting-desc">{{ t('socialForensics.maigret.allSitesHelp') }}</p>
        </div>

        <div class="setting-item">
          <div class="setting-header">
            <Clock size="16" class="text-blue" />
            <label>{{ t('socialForensics.maigret.timeout') }}</label>
            <div class="range-wrapper">
              <input type="range" v-model="timeout" min="5" max="60" class="range-slider" :disabled="isSearching" />
              <span class="range-value">{{ timeout }}s</span>
            </div>
          </div>
          <p class="setting-desc">{{ t('socialForensics.maigret.timeoutHelp') }}</p>
        </div>
      </div>
    </div>
    <div class="progress-area" v-if="isSearching || progressText">
      <div class="progress-header">
        <div class="status-badge" :class="{ 'scanning': isSearching, 'done': !isSearching && results.length > 0, 'error': progressText.includes('Error') }">
          <div class="pulse-dot" v-if="isSearching"></div>
          <span>{{ progressText || (isSearching ? t('socialForensics.maigret.scanning') : t('socialForensics.maigret.idle')) }}</span>
        </div>
        <div class="counter" v-if="results.length > 0">
          <span class="count-number">{{ results.length }}</span> {{ t('socialForensics.maigret.found') }}
        </div>
      </div>
      <div class="progress-track" v-if="isSearching">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>
    <div class="results-section" v-if="results.length > 0">
      <div class="results-grid rich-grid" v-if="richResults.length > 0">
        <div
          v-for="res in richResults"
          :key="res.site"
          class="result-card rich-card"
        >
          <div class="card-header">
            <div class="card-header-left">
              <img :src="getFaviconUrl(res.url)" class="site-favicon" alt="" @error="$event.target.style.display='none'" />
              <div class="card-title-block">
                <h3>{{ res.site }}</h3>
                <a :href="res.url" target="_blank" class="domain-link">
                  {{ getDomain(res.url) }}
                  <ExternalLink size="12" />
                </a>
              </div>
            </div>
            <span class="tag-count-badge">{{ Object.keys(res.tags).length }} fields</span>
          </div>
          <div class="highlight-tags" v-if="Object.keys(getHighlightTags(res.tags)).length > 0">
            <div class="highlight-row" v-for="(val, key) in getHighlightTags(res.tags)" :key="key">
              <span class="hl-label">{{ formatTagLabel(key) }}</span>
              <span class="hl-value" :class="{ 'verified': key === 'is_verified' && val === 'True' }" :title="val">{{ val }}</span>
            </div>
          </div>
          <div class="extra-section" v-if="Object.keys(getExtraTags(res.tags)).length > 0">
            <button class="expand-btn" @click="toggleExpand(res.site)">
              <component :is="expandedCards.has(res.site) ? ChevronUp : ChevronDown" size="14" />
              {{ expandedCards.has(res.site) ? t('socialForensics.maigret.less') : `+${Object.keys(getExtraTags(res.tags)).length} ${t('socialForensics.maigret.more')}` }}
            </button>
            <div class="extra-tags" v-if="expandedCards.has(res.site)">
              <div class="extra-row" v-for="(val, key) in getExtraTags(res.tags)" :key="key">
                <span class="extra-label">{{ formatTagLabel(key) }}</span>
                <span class="extra-value" :title="val">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="basic-section" v-if="basicResults.length > 0">
        <h4 class="section-divider">Other Profiles ({{ basicResults.length }})</h4>
        <div class="results-grid basic-grid">
          <a
            v-for="res in basicResults"
            :key="res.site"
            :href="res.url"
            target="_blank"
            class="result-card basic-card"
          >
            <img :src="getFaviconUrl(res.url)" class="site-favicon-sm" alt="" @error="$event.target.style.display='none'" />
            <div class="basic-info">
              <span class="basic-site">{{ res.site }}</span>
              <span class="basic-url">{{ getDomain(res.url) }}</span>
            </div>
            <ExternalLink size="14" class="link-icon" />
          </a>
        </div>
      </div>
    </div>
    <div class="empty-state" v-if="!isSearching && results.length === 0 && !progressText">
      <div class="empty-icon-wrapper">
        <Search size="48" class="text-muted" />
      </div>
      <h3>{{ t('socialForensics.maigret.readyTitle') }}</h3>
      <p>{{ t('socialForensics.maigret.readyText') }}</p>
      <p class="text-muted" style="font-size: 0.8rem; margin-top: 8px;">{{ t('socialForensics.maigret.poweredBy') }}</p>
    </div>
  </div>
</template>

<style scoped>
.maigret-module {
  display: flex;
  flex-direction: column;
  flex: 1;
}

/* ── Search Panel ─────────────────────────────── */
.search-panel {
  padding: 16px;

  margin-bottom: 20px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);

  padding: 4px;
  position: relative;
}

.icon-user {
  position: absolute;
  left: 16px;
  color: var(--text-muted);
}

.btn-settings {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--text-muted);
  border: 1px solid var(--border-color);
  padding: 12px;

  cursor: pointer;
  transition: var(--transition);
  margin-right: 8px;
}
.btn-settings:hover, .btn-settings.active {
  background: var(--overlay-10);
  color: var(--text-main);
}

.input-wrapper input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-main);
  padding: 14px 16px 14px 48px;
  font-size: 1.1rem;
  outline: none;
}

.btn-search {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--accent-orange);
  color: #000;
  border: none;
  padding: 12px 24px;

  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}
.btn-search:hover { filter: brightness(1.15); }

.btn-stop {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(239, 68, 68, 0.2);
  color: var(--accent-red);
  border: 1px solid rgba(239, 68, 68, 0.4);
  padding: 12px 24px;

  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}
.btn-stop:hover { background: rgba(239, 68, 68, 0.3); }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* ── Settings Panel ───────────────────────────── */
.settings-panel {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.setting-header {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-main);
  font-size: 0.9rem;
  font-weight: 500;
}
.setting-header label:not(.switch) { flex: 1; margin-bottom: 0; }

.setting-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
  padding-left: 28px;
  margin: 0;
}

/* ── Progress ─────────────────────────────────── */
.progress-area {
  margin-bottom: 24px;
  padding: 0 4px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.status-badge.scanning { color: var(--accent-orange); }
.status-badge.done { color: var(--accent-green); }
.status-badge.error { color: var(--accent-red); }

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--accent-orange);

  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(var(--accent-rgb), 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(var(--accent-rgb), 0); }
  100% { box-shadow: 0 0 0 0 rgba(var(--accent-rgb), 0); }
}

.counter {
  font-size: 0.85rem;
  color: var(--text-muted);
}
.count-number {
  color: var(--accent-orange);
  font-weight: 700;
  font-size: 1.1rem;
}

.progress-track {
  height: 3px;
  background: var(--overlay-8);

  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-orange), #ff3366);

  transition: width 0.3s ease;

}

/* ── Results Section ──────────────────────────── */
.results-section {
  padding-bottom: 32px;
}

.results-grid {
  display: grid;
  gap: 16px;
}

.rich-grid {
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  margin-bottom: 32px;
}

.basic-grid {
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}

/* ── Rich Cards ───────────────────────────────── */
.rich-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);

  padding: 0;
  overflow: hidden;
  transition: all 0.25s ease;
}
.rich-card:hover {
  border-color: rgba(var(--accent-rgb), 0.4);

  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.site-favicon {
  width: 24px;
  height: 24px;

  flex-shrink: 0;
}

.card-title-block {
  min-width: 0;
}

.card-title-block h3 {
  color: var(--text-main);
  font-size: 0.95rem;
  margin: 0;
  font-weight: 600;
}

.domain-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-muted);
  font-size: 0.75rem;
  text-decoration: none;
  transition: color 0.2s;
}
.domain-link:hover {
  color: var(--accent-orange);
}

.tag-count-badge {
  background: rgba(var(--accent-rgb), 0.1);
  color: var(--accent-orange);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 8px;

  white-space: nowrap;
  flex-shrink: 0;
}

/* ── Highlight Tags ───────────────────────────── */
.highlight-tags {
  padding: 12px 16px;
}

.highlight-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 5px 0;
  gap: 12px;
}

.highlight-row + .highlight-row {
  border-top: 1px solid var(--border-color);
}

.hl-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  flex-shrink: 0;
}

.hl-value {
  font-size: 0.85rem;
  color: var(--text-main);
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.hl-value.verified {
  color: var(--accent-green, #00ff88);
  font-weight: 600;
}

/* ── Expand Button & Extra Tags ───────────────── */
.extra-section {
  border-top: 1px solid var(--border-color);
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 8px 16px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.78rem;
  cursor: pointer;
  transition: color 0.2s;
}
.expand-btn:hover {
  color: var(--accent-orange);
}

.extra-tags {
  padding: 0 16px 12px;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.extra-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 4px 0;
  gap: 12px;
}

.extra-label {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.extra-value {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

/* ── Basic Cards ──────────────────────────────── */
.section-divider {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.basic-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  padding: 12px 14px;

  text-decoration: none;
  transition: all 0.2s ease;
}
.basic-card:hover {
  border-color: var(--accent-orange);
  background: rgba(var(--accent-rgb), 0.04);
  transform: translateY(-1px);
}

.site-favicon-sm {
  width: 20px;
  height: 20px;

  flex-shrink: 0;
}

.basic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.basic-site {
  color: var(--text-main);
  font-size: 0.88rem;
  font-weight: 500;
}

.basic-url {
  color: var(--text-muted);
  font-size: 0.72rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-icon {
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}
.basic-card:hover .link-icon {
  opacity: 1;
  color: var(--accent-orange);
}

/* ── Empty State ──────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 48px;
  text-align: center;
}

.empty-icon-wrapper {
  width: 96px;
  height: 96px;

  background: var(--overlay-8);
  border: 1px dashed var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: var(--text-main);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-muted);
  max-width: 400px;
}
</style>
