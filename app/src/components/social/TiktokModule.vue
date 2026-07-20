<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Loader2, Hash, BarChart2, Share2, ChevronDown, ChevronUp, Settings, DownloadCloud, FileText } from 'lucide-vue-next'
import { apiService } from '../../services/api'

const { t } = useI18n()

const router = useRouter()

const hashtag = ref('')
const isAnalyzing = ref(false)
const tiktokProgress = ref('')
const tiktokResults = ref([])
const tiktokWs = ref(null)
const tiktokLimit = ref(20)
const tiktokTopN = ref(20)
const showAdvanced = ref(false)

const maxOccurrences = computed(() => {
  if (!tiktokResults.value.length) return 1
  return Math.max(...tiktokResults.value.map(r => r.occurrences))
})

function startTikTokAnalysis() {
  if (!hashtag.value.trim() || isAnalyzing.value) return

  tiktokResults.value = []
  isAnalyzing.value = true
  tiktokProgress.value = t('socialForensics.tiktok.initializing')

  tiktokWs.value = apiService.createTikTokWebSocket()

  tiktokWs.value.onopen = () => {
    let tag = hashtag.value.replace('#', '')
    tiktokWs.value.send(JSON.stringify({
      action: 'analyze',
      hashtag: tag,
      limit: tiktokLimit.value,
      topN: tiktokTopN.value
    }))
    tiktokProgress.value = t('socialForensics.tiktok.analyzing', { hashtag: tag, limit: tiktokLimit.value })
  }

  tiktokWs.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'found') {
      tiktokResults.value.push({
        rank: data.rank,
        tag: data.hashtag,
        occurrences: data.count,
        frequency: data.freq
      })
    } else if (data.type === 'info') {
      tiktokProgress.value = data.text
    } else if (data.type === 'done') {
      isAnalyzing.value = false
      tiktokProgress.value = t('socialForensics.tiktok.complete', { count: data.total })
      if (tiktokWs.value) tiktokWs.value.close()
    } else if (data.type === 'error') {
      isAnalyzing.value = false
      tiktokProgress.value = `${t('socialForensics.tiktok.errorPrefix')} ${data.text}`
      if (tiktokWs.value) tiktokWs.value.close()
    }
  }

  tiktokWs.value.onerror = () => {
    isAnalyzing.value = false
    tiktokProgress.value = t('socialForensics.tiktok.wsError')
  }
}

function stopTikTokAnalysis() {
  if (tiktokWs.value && isAnalyzing.value) {
    tiktokWs.value.close()
    isAnalyzing.value = false
    tiktokProgress.value = t('socialForensics.tiktok.aborted')
  }
}

onUnmounted(() => {
  stopTikTokAnalysis()
})

async function exportToNetworkGraph() {
  if (!tiktokResults.value.length) return

  const rootTag = hashtag.value.replace('#', '')
  const nodes = [{
    id: `node_root_${rootTag}`,
    type: 'custom',
    initialized: false,
    position: { x: 400, y: 300 },
    data: {
      label: `#${rootTag}`,
      type: 'person',
      color: '#FF003C',
      notes: 'Root hashtag analyzed from TikTok'
    }
  }]

  const edges = []
  const radius = 300
  const angleStep = (2 * Math.PI) / tiktokResults.value.length

  tiktokResults.value.forEach((res, i) => {
    const angle = i * angleStep
    const x = 400 + radius * Math.cos(angle)
    const y = 300 + radius * Math.sin(angle)
    const nodeId = `node_${res.tag}`

    nodes.push({
      id: nodeId,
      type: 'custom',
      initialized: false,
      position: { x, y },
      data: {
        label: `#${res.tag}`,
        type: 'org',
        color: '#00FF88',
        notes: `Occurrences: ${res.occurrences}\nFrequency: ${res.frequency}`
      }
    })

    edges.push({
      id: `edge_${rootTag}_${res.tag}`,
      type: 'smoothstep',
      source: `node_root_${rootTag}`,
      target: nodeId,
      sourceHandle: 'right',
      targetHandle: 'left',
      animated: true,
      style: { stroke: 'rgba(255, 255, 255, 0.4)', strokeWidth: Math.max(1, res.frequency * 5) }
    })
  })

  try {
    const filename = `tiktok_network_${rootTag}.json`
    await apiService.saveGraph(filename, { nodes, edges, nextNodeId: nodes.length + 1 })
    router.push('/network')
  } catch (e) {
    console.error("Failed to export graph", e)
  }
}
</script>

<template>
  <div class="tiktok-module">
    <div class="search-panel glass-panel">
      <div class="input-wrapper">
        <Hash class="icon-user" size="20" />
        <input
          v-model="hashtag"
          type="text"
          :placeholder="t('socialForensics.tiktok.placeholder')"
          @keyup.enter="startTikTokAnalysis"
          :disabled="isAnalyzing"
        />
        <button class="btn-settings" @click="showAdvanced = !showAdvanced" :class="{ active: showAdvanced }">
          <Settings size="18" />
        </button>
        <button class="btn-search" @click="startTikTokAnalysis" v-if="!isAnalyzing">
          <BarChart2 size="18" /> {{ t('socialForensics.tiktok.search') }}
        </button>
        <button class="btn-stop" @click="stopTikTokAnalysis" v-else>
          <Loader2 size="18" class="spin" /> {{ t('socialForensics.tiktok.abort') }}
        </button>
      </div>
      <div class="settings-panel" v-if="showAdvanced">
        <div class="setting-item">
          <div class="setting-header">
            <DownloadCloud size="16" class="text-blue" />
            <label>{{ t('socialForensics.tiktok.postsToScrape') }}</label>
            <div class="range-wrapper">
              <input type="range" v-model="tiktokLimit" min="10" max="1000" class="range-slider" :disabled="isAnalyzing" />
              <span class="range-value">{{ tiktokLimit }}</span>
            </div>
          </div>
          <p class="setting-desc">{{ t('socialForensics.tiktok.postsHelp') }}</p>
        </div>

        <div class="setting-item">
          <div class="setting-header">
            <FileText size="16" class="text-orange" />
            <label>{{ t('socialForensics.tiktok.hashtagsToShow') }}</label>
            <div class="range-wrapper">
              <input type="range" v-model="tiktokTopN" min="5" max="100" class="range-slider" :disabled="isAnalyzing" />
              <span class="range-value">{{ tiktokTopN }}</span>
            </div>
          </div>
          <p class="setting-desc">{{ t('socialForensics.tiktok.hashtagsHelp') }}</p>
        </div>
      </div>
    </div>
    <div class="progress-area" v-if="isAnalyzing || tiktokResults.length > 0 || tiktokProgress">
      <div class="progress-header">
        <div class="status-badge" :class="{ 'scanning': isAnalyzing, 'done': !isAnalyzing && tiktokResults.length > 0, 'error': tiktokProgress.includes('Error') }">
          <div class="pulse-dot" v-if="isAnalyzing"></div>
          <span>{{ tiktokProgress || (isAnalyzing ? t('socialForensics.tiktok.scanning') : t('socialForensics.tiktok.idle')) }}</span>
        </div>
        <div class="stats-actions" v-if="tiktokResults.length > 0">
          <div class="counter">
            <span class="count-number">{{ tiktokResults.length }}</span> {{ t('socialForensics.tiktok.hashtags') }}
          </div>
          <button class="btn-export" @click="exportToNetworkGraph" :title="t('socialForensics.tiktok.graphTitle')">
            <Share2 size="14" /> {{ t('socialForensics.tiktok.graph') }}
          </button>
        </div>
      </div>
      <div class="progress-track" v-if="isAnalyzing">
        <div class="progress-fill indeterminate"></div>
      </div>
    </div>
    <div class="results-table-container glass-panel" v-if="tiktokResults.length > 0">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-rank">#</th>
            <th>{{ t('socialForensics.tiktok.coOccurringHashtag') }}</th>
            <th class="col-occ">{{ t('socialForensics.tiktok.occurrences') }}</th>
            <th class="col-freq">{{ t('socialForensics.tiktok.frequency') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(res, idx) in tiktokResults" :key="idx">
            <td class="rank-cell">{{ idx + 1 }}</td>
            <td>
              <span class="hashtag-label">#{{ res.tag }}</span>
            </td>
            <td class="occ-cell">
              <span class="occ-value">{{ res.occurrences }}</span>
            </td>
            <td>
              <div class="freq-bar-container">
                <div class="freq-bar-track">
                  <div
                    class="freq-bar-fill"
                    :style="{ width: `${(res.occurrences / maxOccurrences) * 100}%` }"
                  ></div>
                </div>
                <span class="freq-text">{{ (parseFloat(res.frequency) * 100).toFixed(0) }}%</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="empty-state" v-if="!isAnalyzing && tiktokResults.length === 0 && !tiktokProgress">
      <div class="empty-icon-wrapper">
        <Hash size="48" class="text-muted" />
      </div>
      <h3>{{ t('socialForensics.tiktok.readyTitle') }}</h3>
      <p>{{ t('socialForensics.tiktok.readyText') }}</p>
      <p class="text-muted" style="font-size: 0.8rem; margin-top: 8px;">{{ t('socialForensics.tiktok.poweredBy') }}</p>
    </div>
  </div>
</template>

<style scoped>
.tiktok-module {
  display: flex;
  flex-direction: column;
  flex: 1;
}

/* ── Search Panel ─────────────────────────────── */
.search-panel {
  padding: 16px;

  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
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
.setting-header label { flex: 1; margin-bottom: 0; }

.setting-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
  padding-left: 28px;
  margin: 0;
}

/* ── Progress ─────────────────────────────────── */

.option-group .help-text {
  font-size: 0.72rem;
  color: var(--text-muted);
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

.stats-actions {
  display: flex;
  align-items: center;
  gap: 12px;
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

.btn-export {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(var(--accent-rgb), 0.08);
  border: 1px solid rgba(var(--accent-rgb), 0.25);
  color: var(--accent-orange);
  padding: 5px 10px;

  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-export:hover {
  background: rgba(var(--accent-rgb), 0.15);
  transform: translateY(-1px);
}

.progress-track {
  height: 3px;
  background: var(--overlay-8);

  overflow: hidden;
}
.progress-fill.indeterminate {
  height: 100%;
  width: 30%;
  background: linear-gradient(90deg, var(--accent-orange), #ff3366);

  animation: indeterminate 1.4s ease-in-out infinite;

}
@keyframes indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

/* ── Results Table ────────────────────────────── */
.results-table-container {
  overflow-x: auto;

  padding: 0;
  margin-bottom: 32px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.col-rank { width: 50px; }
.col-occ { width: 100px; }
.col-freq { width: 220px; }

.data-table th {
  padding: 14px 16px;
  text-align: left;
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-panel);
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr {
  transition: background 0.15s;
}
.data-table tr:hover {
  background: rgba(var(--accent-rgb), 0.03);
}

.rank-cell {
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
}

.hashtag-label {
  background: rgba(var(--accent-rgb), 0.08);
  color: var(--accent-orange);
  padding: 4px 10px;

  font-weight: 500;
  font-size: 0.88rem;
  border: 1px solid rgba(var(--accent-rgb), 0.15);
}

.occ-cell {
  text-align: center;
}

.occ-value {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--text-main);
}

.freq-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.freq-bar-track {
  flex: 1;
  height: 6px;
  background: var(--overlay-8);

  overflow: hidden;
}

.freq-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-orange), #ff3366);

  transition: width 0.4s ease;

}

.freq-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 38px;
  text-align: right;
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
