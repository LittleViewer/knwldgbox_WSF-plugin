<script setup>
import { Building, Calendar, Globe, Server } from 'lucide-vue-next'
import SendToGraphButton from '../SendToGraphButton.vue'

defineProps({
  whois: { type: Object, required: true }
})

function formatDate(date) {
  if (!date) return 'N/A'
  if (Array.isArray(date)) {
    return new Date(date[0]).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  }
  return new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatList(item) {
  if (!item) return 'N/A'
  if (Array.isArray(item)) return item.join(', ')
  return item
}

function normalizeList(item) {
  if (!item) return []
  return Array.isArray(item) ? item : [item]
}
</script>

<template>
  <div class="result-card glass-panel">
    <div class="card-header">
      <Globe size="18" class="text-purple" />
      <h3>Domain Overview</h3>
    </div>
    <div class="card-body">
      <div class="data-row">
        <span class="label">Domain Name</span>
        <span class="value highlight">{{ formatList(whois.domain_name) }}</span>
      </div>
      <div class="data-row">
        <span class="label">Registrar</span>
        <span class="value">{{ formatList(whois.registrar) }}</span>
      </div>
      <div class="data-row">
        <span class="label">Whois Server</span>
        <span class="value">{{ formatList(whois.whois_server) }}</span>
      </div>
    </div>
  </div>

  <div class="result-card glass-panel">
    <div class="card-header">
      <Calendar size="18" class="text-orange" />
      <h3>Important Dates</h3>
    </div>
    <div class="card-body">
      <div class="data-row">
        <span class="label">Creation Date</span>
        <div class="val-group">
          <span class="value">{{ formatDate(whois.creation_date) }}</span>
          <SendToGraphButton small :label="formatDate(whois.creation_date)" iconName="Calendar" color="#F97316" notes="Creation Date" v-if="whois.creation_date" />
        </div>
      </div>
      <div class="data-row">
        <span class="label">Updated Date</span>
        <span class="value">{{ formatDate(whois.updated_date) }}</span>
      </div>
      <div class="data-row">
        <span class="label">Expiration Date</span>
        <div class="val-group">
          <span class="value text-red strong">{{ formatDate(whois.expiration_date) }}</span>
          <SendToGraphButton small :label="formatDate(whois.expiration_date)" iconName="Calendar" color="#EF4444" notes="Expiration Date" v-if="whois.expiration_date" />
        </div>
      </div>
    </div>
  </div>

  <div class="result-card glass-panel">
    <div class="card-header">
      <Server size="18" class="text-green" />
      <h3>Technical Info</h3>
    </div>
    <div class="card-body">
      <div class="data-row stack">
        <span class="label">Name Servers</span>
        <div class="value tags">
          <span class="tag" v-for="ns in normalizeList(whois.name_servers)" :key="ns">
            {{ ns }}
          </span>
        </div>
      </div>
      <div class="data-row stack mt-3">
        <span class="label">DNSSEC</span>
        <span class="value">{{ formatList(whois.dnssec) }}</span>
      </div>
    </div>
  </div>

  <div class="result-card glass-panel">
    <div class="card-header">
      <Building size="18" class="text-blue" />
      <h3>Registrant Info</h3>
    </div>
    <div class="card-body">
      <div class="data-row">
        <span class="label">Organization</span>
        <span class="value">{{ formatList(whois.org) }}</span>
      </div>
      <div class="data-row">
        <span class="label">State/Province</span>
        <span class="value">{{ formatList(whois.state) }}</span>
      </div>
      <div class="data-row">
        <span class="label">Country</span>
        <span class="value">{{ formatList(whois.country) }}</span>
      </div>
      <div class="data-row">
        <span class="label">Emails</span>
        <div class="val-group">
          <span class="value text-orange">{{ formatList(whois.emails) }}</span>
          <SendToGraphButton small :label="formatList(whois.emails)" iconName="Mail" color="#F97316" notes="Registrant Email" v-if="whois.emails" />
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

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.val-group {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
  text-align: right;
}

.data-row.stack {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.data-row.stack .value {
  text-align: left;
}

.label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 500;
  flex-shrink: 0;
}

.value {
  font-size: 0.95rem;
  color: var(--text-main);
  font-weight: 500;
  text-align: right;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.highlight {
  color: var(--accent-purple);
  font-weight: 700;
  font-size: 1.1rem;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: var(--overlay-8);
  border: 1px solid var(--border-color);
  padding: 4px 10px;

  font-size: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
}

.strong {
  font-weight: 600;
}

.mt-3 {
  margin-top: 12px;
}

.text-purple { color: var(--accent-purple); }
.text-orange { color: var(--accent-orange); }
.text-red { color: var(--accent-red); }
.text-green { color: var(--accent-green); }
.text-blue { color: var(--accent-blue); }
</style>
