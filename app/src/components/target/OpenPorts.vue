<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { DoorOpen } from 'lucide-vue-next'

const props = defineProps({
  ports: { type: Array, required: true }
})

const portMap = {
  21: "FTP",
  22: "SSH",
  23: "Telnet",
  25: "SMTP",
  53: "DNS",
  80: "HTTP",
  110: "POP3",
  143: "IMAP",
  443: "HTTPS",
  465: "SMTPS",
  993: "IMAPS",
  995: "POP3S",
  3306: "MySQL",
  3389: "RDP",
  5432: "PostgreSQL",
  8080: "HTTP-Alt",
  8443: "HTTPS-Alt"
}
</script>

<template>
  <div class="result-card glass-panel ports-card">
    <div class="card-header">
      <DoorOpen size="20" class="text-orange" />
      <h3>{{ t('targetAnalysis.components.openPorts.title') }}</h3>
    </div>
    
    <div class="card-body">
      <div v-if="ports.length === 0" class="empty-msg">
        {{ t('targetAnalysis.components.openPorts.empty') }}
      </div>
      
      <div class="ports-grid" v-else>
        <div v-for="port in ports" :key="port" class="port-badge">
          <span class="port-num mono">{{ port }}</span>
          <span class="port-name">{{ portMap[port] || t('targetAnalysis.components.openPorts.unknown') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ports-card {
  display: flex;
  flex-direction: column;
}

.empty-msg {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}

.ports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.port-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: rgba(var(--accent-rgb), 0.1);
  border: 1px solid rgba(var(--accent-rgb), 0.3);
  padding: 10px;

  transition: all 0.2s;
}

.port-badge:hover {
  background: rgba(var(--accent-rgb), 0.2);
  transform: translateY(-2px);
}

.port-num {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--accent-orange);
}

.port-name {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--text-main);
  letter-spacing: 0.05em;
}
</style>
