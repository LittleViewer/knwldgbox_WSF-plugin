<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Share2, Check, Plus } from 'lucide-vue-next'
import { sendToGraph, sendMultipleToGraph } from '../utils/graphStore.js'
import { apiService } from '../services/api'

const { t } = useI18n()

const props = defineProps({
  label: { type: String, required: true },
  iconName: { type: String, default: 'Box' },
  color: { type: String, default: '#3B82F6' },
  notes: { type: String, default: '' },
  small: { type: Boolean, default: false },
  nodes: { type: Array, default: null },
  edges: { type: Array, default: null }
})

const sent = ref(false)
const showMenu = ref(false)
const graphs = ref([])
const menuX = ref(0)
const menuY = ref(0)

async function fetchGraphs() {
  try {
    const data = await apiService.listGraphs()
    graphs.value = data.graphs || []
  } catch (e) {
    console.error("Failed to fetch graphs", e)
  }
}

async function handleSendClick(e) {
  e.preventDefault()
  e.stopPropagation()

  if (sent.value) return

  await fetchGraphs()
  menuX.value = e.clientX
  menuY.value = e.clientY
  showMenu.value = true
}

async function confirmSend(targetFilename) {
  showMenu.value = false
  
  if (props.nodes && props.edges) {
    await sendMultipleToGraph(props.nodes, props.edges, targetFilename)
  } else {
    await sendToGraph(props.label, props.iconName, props.color, props.notes, targetFilename)
  }
  
  sent.value = true
  setTimeout(() => {
    sent.value = false
  }, 2000)
}

function handleClickOutside(e) {
  if (showMenu.value && !e.target.closest('.send-graph-menu') && !e.target.closest('.send-to-graph-btn')) {
    showMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div style="display: inline-block;">
    <button
      class="send-to-graph-btn"
      :class="{ 'sent': sent, 'small': small }"
      @click="handleSendClick"
      :title="sent ? t('sendToGraph.sent') : t('sendToGraph.send')"
    >
      <Check size="16" v-if="sent" />
      <Share2 size="16" v-else />
    </button>

    <Teleport to="body">
      <div 
        v-if="showMenu" 
        class="send-graph-menu"
        :style="{ top: `${menuY + 10}px`, left: `${menuX - 100}px` }"
      >
        <div class="menu-header">{{ $t('sendToGraph.menuHeader') }}</div>
        <div class="menu-items">
          <button class="menu-item new-graph" @click.stop="confirmSend(null)">
            <Plus size="14" />
            <span>{{ $t('sendToGraph.newGraph') }}</span>
          </button>
          <div class="menu-divider" v-if="graphs.length > 0"></div>
          <button 
            v-for="g in graphs" 
            :key="g.filename"
            class="menu-item" 
            @click.stop="confirmSend(g.filename)"
          >
            <Share2 size="14" />
            <span class="truncate">{{ g.filename.replace('.json', '') }}</span>
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.send-to-graph-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;

  background: var(--overlay-8);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-to-graph-btn.small {
  width: 24px;
  height: 24px;

}

.send-to-graph-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: var(--accent-blue);
  transform: translateY(-2px);
}

.send-to-graph-btn.sent {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--accent-green);
  transform: none;
}

.send-graph-menu {
  position: fixed;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  width: 200px;
  max-height: 300px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.menu-header {
  padding: 10px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-color);
  background: var(--overlay-8);
}

.menu-items {
  overflow-y: auto;
  padding: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  background: transparent;
  border: none;
  color: var(--text-main);
  font-size: 0.85rem;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
}

.menu-item:hover {
  background: var(--overlay-8);
  color: var(--accent-blue);
}

.menu-item.new-graph {
  color: var(--accent-green);
}

.menu-item.new-graph:hover {
  background: rgba(16, 185, 129, 0.1);
}

.menu-divider {
  height: 1px;
  background: var(--border-color);
  margin: 4px 0;
}

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
