<script setup>
import { Calendar, Key, Shield } from 'lucide-vue-next'
import SendToGraphButton from '../SendToGraphButton.vue'

defineProps({
  urlscan: { type: Object, required: true }
})
</script>

<template>
  <div class="result-card glass-panel">
    <div class="card-header">
      <Shield size="18" class="text-green" />
      <h3>Scan Metrics</h3>
    </div>
    <div class="card-body">
      <div class="stats-boxes">
        <div class="stat-box">
          <span class="stat-num">{{ urlscan.stats?.requests || 0 }}</span>
          <span class="stat-label">Requests</span>
        </div>
        <div class="stat-box">
          <span class="stat-num">{{ urlscan.stats?.uniqIPs || 0 }}</span>
          <span class="stat-label">Unique IPs</span>
        </div>
        <div class="stat-box">
          <span class="stat-num">{{ urlscan.stats?.uniqCountries || 0 }}</span>
          <span class="stat-label">Countries</span>
        </div>
      </div>

      <div v-if="urlscan.detailed" class="detailed-metrics mt-4">
        <div class="data-row stack" v-if="urlscan.detailed.lists?.countries?.length">
          <span class="label">Countries ({{ urlscan.detailed.lists.countries.length }})</span>
          <div class="value tags">
            <span class="tag" v-for="country in urlscan.detailed.lists.countries" :key="country">{{ country }}</span>
          </div>
        </div>

        <div class="data-row stack mt-3" v-if="urlscan.detailed.lists?.ips?.length">
          <span class="label">IP Addresses ({{ urlscan.detailed.lists.ips.length }})</span>
          <div class="value tags">
            <span class="tag tag-blue" v-for="ip in urlscan.detailed.lists.ips.slice(0, 15)" :key="ip">
              {{ ip }}
              <SendToGraphButton small :label="ip" iconName="Server" color="#60A5FA" notes="IP Address" class="inline-btn" />
            </span>
            <span class="tag" v-if="urlscan.detailed.lists.ips.length > 15">...</span>
          </div>
        </div>

        <div class="data-row stack mt-3" v-if="urlscan.detailed.lists?.domains?.length">
          <span class="label">Domains Contacted ({{ urlscan.detailed.lists.domains.length }})</span>
          <div class="value tags">
            <span class="tag tag-orange" v-for="domain in urlscan.detailed.lists.domains.slice(0, 10)" :key="domain">
              {{ domain }}
              <SendToGraphButton small :label="domain" iconName="Globe" color="#FBBF24" notes="Domain" class="inline-btn" />
            </span>
            <span class="tag" v-if="urlscan.detailed.lists.domains.length > 10">...</span>
          </div>
        </div>

        <div class="data-row stack mt-3" v-if="urlscan.detailed.meta?.processors?.tech?.length">
          <span class="label">Detected Technologies</span>
          <div class="value tags">
            <span class="tag tag-green" v-for="tech in urlscan.detailed.meta.processors.tech" :key="tech.name">{{ tech.name }}</span>
          </div>
        </div>

        <div class="data-row stack mt-3" v-if="urlscan.detailed.lists?.certificates?.length">
          <span class="label">Certificates ({{ urlscan.detailed.lists.certificates.length }})</span>
          <div class="certs-list">
            <div class="cert-item" v-for="(cert, idx) in urlscan.detailed.lists.certificates.slice(0, 5)" :key="idx">
              <div class="cert-main">
                <div class="cert-subject">{{ cert.subjectName || cert.subject }}</div>
                <div class="cert-issuer">{{ cert.issuerName || cert.issuer }}</div>
              </div>
              <div class="cert-dates" v-if="cert.validFrom && cert.validTo">
                <Calendar size="12" />
                {{ new Date(cert.validFrom * 1000).toISOString().split('T')[0] }}
                &rarr;
                {{ new Date(cert.validTo * 1000).toISOString().split('T')[0] }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="api-key-prompt mt-4">
        <Key size="14" />
        <span>Configure urlscan.io API Key in Settings to see exact IPs, Countries, and Technologies.</span>
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

.stats-boxes {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.stat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--overlay-8);
  padding: 16px;

  border: 1px solid var(--border-color);
}

.stat-num {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-main);
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-top: 4px;
}

.detailed-metrics {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
  margin-top: 16px;
}

.data-row.stack {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 500;
}

.value {
  font-size: 0.95rem;
  color: var(--text-main);
  font-weight: 500;
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
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

:deep(.inline-btn) {
  margin-left: 2px;
  background: transparent;
  border-color: transparent;
}
:deep(.inline-btn:hover) {
  background: var(--overlay-10);
}

.tag-blue { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); color: #60A5FA; }
.tag-orange { background: rgba(var(--accent-rgb), 0.1); border-color: rgba(var(--accent-rgb), 0.3); color: var(--accent-orange); }
.tag-green { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); color: #34D399; }

.certs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.cert-item {
  background: var(--overlay-8);
  border: 1px solid var(--border-color);
  padding: 12px;

  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.cert-main {
  display: flex;
  flex-direction: column;
}

.cert-subject {
  font-weight: 600;
  color: var(--text-main);
  font-size: 0.9rem;
}

.cert-issuer {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.cert-dates {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--accent-orange);
  background: rgba(var(--accent-rgb), 0.1);
  padding: 4px 8px;

}

.api-key-prompt {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(var(--accent-rgb), 0.05);
  border: 1px dashed rgba(var(--accent-rgb), 0.3);

  color: var(--accent-orange);
  font-size: 0.8rem;
  margin-top: 16px;
}

.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 24px; }
.text-green { color: var(--accent-green); }
</style>
