<script setup>
import { useI18n } from 'vue-i18n'
import { Search, ListTree } from 'lucide-vue-next'

const { t } = useI18n()

defineProps({
  requests: { type: Array, required: true }
})

const emit = defineEmits(['select'])

function formatRequestHost(url) {
  if (!url) return 'N/A'
  try {
    return new URL(url).hostname
  } catch {
    return url.replace(/^https?:\/\//, '').split('/')[0] || url
  }
}

function formatMimeType(type) {
  if (!type) return 'N/A'
  return type.replace('application/', '').replace('image/', '').replace('text/', '')
}

function responseStatus(request) {
  return request.response?.response?.status || request.request?.response?.status || 'N/A'
}

function isErrorStatus(request) {
  const status = request.response?.response?.status || request.request?.response?.status
  return status >= 400
}
</script>

<template>
  <div class="result-card glass-panel transactions-card">
    <div class="card-header">
      <ListTree size="18" class="text-orange" />
      <h3>{{ t('targetComponents.httpTransactions.title') }} ({{ requests.length }})</h3>
    </div>
    <div class="card-body p-0">
      <div class="transactions-table-wrapper">
        <table class="transactions-table">
          <thead>
            <tr>
              <th>{{ t('targetComponents.httpTransactions.method') }}</th>
              <th>{{ t('targetComponents.httpTransactions.status') }}</th>
              <th>{{ t('targetComponents.httpTransactions.resource') }}</th>
              <th>{{ t('targetComponents.httpTransactions.type') }}</th>
              <th>{{ t('targetComponents.httpTransactions.ipAsn') }}</th>
              <th>{{ t('targetComponents.httpTransactions.details') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(request, idx) in requests" :key="idx" class="tx-row" @click="emit('select', request)">
              <td>
                <span :class="['method-badge', request.request?.request?.method?.toLowerCase()]">
                  {{ request.request?.request?.method || 'UNK' }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', isErrorStatus(request) ? 'error' : 'ok']">
                  {{ responseStatus(request) }}
                </span>
              </td>
              <td class="resource-cell">
                <a
                  v-if="request.request?.request?.url"
                  :href="request.request.request.url"
                  target="_blank"
                  @click.stop
                  class="url-path truncate text-blue"
                  :title="request.request.request.url"
                >
                  {{ formatRequestHost(request.request.request.url) }}
                </a>
                <span v-else class="text-muted">N/A</span>
              </td>
              <td class="text-muted mime-cell">
                {{ formatMimeType(request.response?.response?.mimeType || request.request?.response?.mimeType) }}
              </td>
              <td>
                <div class="ip-cell">
                  <span class="text-blue">{{ request.response?.asn?.ip || request.serverIPAddress || 'N/A' }}</span>
                  <span class="asn-name text-muted" v-if="request.response?.asn?.name || request.response?.asnname">
                    {{ request.response?.asn?.name || request.response?.asnname }}
                  </span>
                </div>
              </td>
              <td>
                <button class="btn-expand" @click.stop="emit('select', request)">
                  <Search size="14" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
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

.p-0 {
  padding: 0 !important;
}

.transactions-card {
  height: 420px;
  min-width: 0;
}

.transactions-card .card-body {
  flex: 1;
  min-height: 0;
}

.transactions-table-wrapper {
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;

}

.transactions-table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.8rem;
}

.transactions-table th {
  padding: 8px 10px;
  background: var(--overlay-8);
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 10;
}

.transactions-table td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.transactions-table th:nth-child(1),
.transactions-table td:nth-child(1) {
  width: 68px;
}

.transactions-table th:nth-child(2),
.transactions-table td:nth-child(2) {
  width: 64px;
}

.transactions-table th:nth-child(3),
.transactions-table td:nth-child(3) {
  width: 28%;
}

.transactions-table th:nth-child(4),
.transactions-table td:nth-child(4) {
  width: 18%;
}

.transactions-table th:nth-child(5),
.transactions-table td:nth-child(5) {
  width: 25%;
}

.transactions-table th:nth-child(6),
.transactions-table td:nth-child(6) {
  width: 56px;
}

.tx-row {
  cursor: pointer;
  transition: background 0.2s;
}

.tx-row:hover {
  background: var(--overlay-8);
}

.url-path {
  display: block;
  text-decoration: none;
}

.url-path:hover {
  text-decoration: underline;
}

.resource-cell {
  min-width: 0;
}

.truncate,
.mime-cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.method-badge {
  padding: 4px 8px;

  font-weight: 700;
  font-size: 0.75rem;
  background: var(--overlay-10);
}

.method-badge.get { color: #34D399; background: rgba(16, 185, 129, 0.1); }
.method-badge.post { color: var(--accent-orange); background: rgba(var(--accent-rgb), 0.1); }
.method-badge.options { color: #60A5FA; background: rgba(59, 130, 246, 0.1); }

.status-badge {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}

.status-badge.ok { color: #34D399; }
.status-badge.error { color: var(--accent-red); }

.ip-cell {
  display: flex;
  flex-direction: column;
}

.asn-name {
  font-size: 0.7rem;
}

.btn-expand {
  background: rgba(var(--accent-rgb), 0.1);
  color: var(--accent-orange);
  border: 1px solid rgba(var(--accent-rgb), 0.3);
  padding: 6px;

  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-expand:hover {
  background: var(--accent-orange);
  color: #000;
}

.text-orange { color: var(--accent-orange); }
.text-blue { color: var(--accent-blue); }
.text-muted { color: var(--text-muted); }
</style>
