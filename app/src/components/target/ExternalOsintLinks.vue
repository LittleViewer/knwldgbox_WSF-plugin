<script setup>
import { ExternalLink, Search, Shield, Server, FileSearch, Code, Eye, Mail, Lock } from 'lucide-vue-next'

const props = defineProps({
  domain: { type: String, required: true }
})

const getLinks = (d) => [
  { name: 'VirusTotal', url: `https://www.virustotal.com/gui/domain/${d}/detection`, icon: Shield, color: 'text-blue' },
  { name: 'Shodan', url: `https://www.shodan.io/search?query=${d}`, icon: Search, color: 'text-red' },
  { name: 'SecurityTrails', url: `https://securitytrails.com/domain/${d}/dns`, icon: Server, color: 'text-green' },
  { name: 'Censys', url: `https://search.censys.io/search?resource=hosts&q=${d}`, icon: Eye, color: 'text-orange' },
  { name: 'BuiltWith', url: `https://builtwith.com/${d}`, icon: Code, color: 'text-purple' },
  { name: 'AlienVault OTX', url: `https://otx.alienvault.com/indicator/domain/${d}`, icon: Shield, color: 'text-blue' },
  { name: 'Hunter.io (Emails)', url: `https://hunter.io/search/${d}`, icon: Mail, color: 'text-orange' },
  { name: 'CRT.sh (Certs)', url: `https://crt.sh/?q=%.${d}`, icon: Lock, color: 'text-green' },
  { name: 'ViewDNS', url: `https://viewdns.info/dnsreport/?domain=${d}`, icon: FileSearch, color: 'text-purple' }
]
</script>

<template>
  <div class="result-card glass-panel osint-card">
    <div class="card-header">
      <ExternalLink size="20" class="text-blue" />
      <h3>External OSINT Lookups</h3>
    </div>
    
    <div class="card-body">
      <div class="links-grid">
        <a 
          v-for="link in getLinks(domain)" 
          :key="link.name" 
          :href="link.url" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="osint-btn"
        >
          <component :is="link.icon" size="14" :class="link.color" />
          <span>{{ link.name }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.osint-card { display: flex; flex-direction: column; }
.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
}
.osint-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--overlay-3);
  border: 1px solid var(--overlay-10);
  padding: 8px 10px;

  text-decoration: none;
  color: var(--text-main);
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s;
}
.osint-btn:hover {
  background: var(--overlay-8);
  border-color: var(--overlay-20);
  transform: translateY(-1px);
}
.text-blue { color: var(--accent-blue); }
.text-red { color: var(--accent-red); }
.text-green { color: var(--accent-green); }
.text-orange { color: #f97316; }
.text-purple { color: #8b5cf6; }
</style>
