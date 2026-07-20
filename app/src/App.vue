<script setup>
import { ref, onMounted, computed, markRaw, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import draggable from 'vuedraggable'
import {
  ShieldAlert,
  Crosshair,
  GlobeLock,
  Activity,
  Users,
  Settings,
  Cpu,
  ChevronRight,
  ListTree,
  Menu,
  Image as ImageIcon,
  Map as MapIcon,
  DownloadCloud,
  Search,
  Sun,
  Moon,
  MessageSquare,
  Aperture
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const { t, locale } = useI18n()

const baseNavItems = [
  { id: 'dashboard', route: '/', icon: markRaw(Activity), i18nKey: 'sidebar.dashboard' },
  { id: 'monitoring', route: '/monitoring', icon: markRaw(ListTree), i18nKey: 'sidebar.monitoring' },
  { id: 'target', route: '/target', icon: markRaw(Crosshair), i18nKey: 'sidebar.targetAnalysis' },
  { id: 'network', route: '/network', icon: markRaw(GlobeLock), i18nKey: 'sidebar.networkGraph' },
  { id: 'social', route: '/social', icon: markRaw(Users), i18nKey: 'sidebar.socialForensics' },
  { id: 'leaks', route: '/leaks', icon: markRaw(ShieldAlert), i18nKey: 'sidebar.dataLeaks' },
  { id: 'dorks', route: '/dorks', icon: markRaw(Search), i18nKey: 'sidebar.dorkBuilder' },
  { id: 'tools', route: '/tools', icon: markRaw(ImageIcon), i18nKey: 'sidebar.knwldgTools' },
  { id: 'downloaders', route: '/downloaders', icon: markRaw(DownloadCloud), i18nKey: 'sidebar.mediaDownloaders' },
  { id: 'archives', route: '/archives', icon: markRaw(Activity), i18nKey: 'sidebar.archives' },
  { id: 'osintMap', route: '/osint-map', icon: markRaw(MapIcon), i18nKey: 'sidebar.osintMap' },
  { id: 'imageForensics', route: '/image-forensics', icon: markRaw(Aperture), i18nKey: 'sidebar.imageForensics' },
  { id: 'aichat', route: '/ai-chat', icon: markRaw(MessageSquare), i18nKey: 'sidebar.aiChatbot' },
]

const savedOrder = localStorage.getItem('knwldg_sidebar_order')
let initialOrder = []
if (savedOrder) {
  try { initialOrder = JSON.parse(savedOrder) } catch(e) {}
}
if (!initialOrder || initialOrder.length === 0) {
  initialOrder = baseNavItems.map(item => item.id)
}

const initialItems = []
initialOrder.forEach(id => {
  const item = baseNavItems.find(i => i.id === id)
  if (item) initialItems.push(item)
})

baseNavItems.forEach(item => {
  if (!initialItems.find(i => i.id === item.id)) {
    initialItems.push(item)
  }
})

const orderedNavItems = ref(initialItems)

watch(orderedNavItems, (newVal) => {
  if (newVal.length > 0) {
    const order = newVal.map(item => item.id)
    localStorage.setItem('knwldg_sidebar_order', JSON.stringify(order))
  }
}, { deep: true })

const toggleLanguage = () => {
  const newLang = locale.value === 'en' ? 'fr' : 'en'
  locale.value = newLang
  localStorage.setItem('knwldg_lang', newLang)
}

const isSidebarVisible = ref(window.innerWidth > 768)
const isLightMode = ref(localStorage.getItem('knwldg_light_mode') === 'true')

function toggleLightMode() {
  isLightMode.value = !isLightMode.value
  document.body.classList.toggle('light-mode', isLightMode.value)
  localStorage.setItem('knwldg_light_mode', isLightMode.value)
}

onMounted(() => {
  if (isLightMode.value) {
    document.body.classList.add('light-mode')
  }

  const savedCustom = localStorage.getItem('knwldg_app_customization')
  if (savedCustom) {
    try {
      const prefs = JSON.parse(savedCustom)

      // Apply app theme
      if (prefs.appTheme) {
        document.body.classList.remove('theme-brutalist', 'theme-enterprise', 'theme-cyber')
        document.body.classList.add(prefs.appTheme)
      }

      // Apply theme color
      if (prefs.accentColor && prefs.accentColor !== 'default') {
        document.body.style.setProperty('--accent-orange', prefs.accentColor)
        // Convert hex to rgb for rgba() usage
        const hex = prefs.accentColor.replace('#', '')
        const r = parseInt(hex.substring(0, 2), 16)
        const g = parseInt(hex.substring(2, 4), 16)
        const b = parseInt(hex.substring(4, 6), 16)
        if (!isNaN(r) && !isNaN(g) && !isNaN(b)) {
          document.body.style.setProperty('--accent-rgb', `${r}, ${g}, ${b}`)
        }
      } else {
        document.body.style.removeProperty('--accent-orange')
        document.body.style.removeProperty('--accent-rgb')
      }

      // Apply Typography
      if (prefs.fontFamily) {
        if (prefs.fontFamily === 'custom' && prefs.customFontData) {
          let style = document.getElementById('custom-font-style')
          if (!style) {
            style = document.createElement('style')
            style.id = 'custom-font-style'
            document.head.appendChild(style)
          }
          style.innerHTML = `
            @font-face {
              font-family: 'UserCustomFont';
              src: url('${prefs.customFontData}');
            }
          `
          document.body.style.fontFamily = "'UserCustomFont', monospace"
        } else {
          document.body.style.fontFamily = `"${prefs.fontFamily}", monospace`
        }
      }

      // Handle default startup view
      // Only redirect if they are landing on the base path (Dashboard)
      // so we don't break deep links or manual navigation
      if (prefs.defaultView && prefs.defaultView !== '/' && window.location.pathname === '/') {
        router.push(prefs.defaultView)
      }
    } catch (e) {
      console.error("Failed to apply customization preferences:", e)
    }
  }
})
</script>

<template>
  <!-- Sidebar -->
  <aside class="sidebar glass-panel" v-show="isSidebarVisible">
    <div class="brand">
      <div class="logo-icon">
        <Cpu class="text-orange" />
      </div>
      <div class="brand-text">
        <span class="brand-title">{{ $t('sidebar.brandTitle') }}</span>
        <span class="brand-subtitle">{{ $t('sidebar.brandSubtitle') }}</span>
      </div>
    </div>

    <div class="pinned-menu-header">
      <div class="nav-section">{{ $t('sidebar.mainMenu') }}</div>
      <button class="nav-item collapse-btn" @click="isSidebarVisible = false" :title="$t('sidebar.hideMenu')">
        <Menu class="nav-icon" size="20" />
        <span>{{ $t('sidebar.hideMenu') }}</span>
      </button>
    </div>

    <nav class="nav-menu">
      <draggable
        v-model="orderedNavItems"
        item-key="id"
        ghost-class="ghost-nav-item"
        class="nav-items-wrapper"
        :animation="200"
        :delay="200"
        :delayOnTouchOnly="true"
      >
        <template #item="{ element }">
          <router-link
            :to="element.route"
            :class="['nav-item', { active: route.path === element.route }]"
          >
            <component :is="element.icon" class="nav-icon" size="20" />
            <span>{{ $t(element.i18nKey) }}</span>
            <ChevronRight v-if="route.path === element.route" class="active-indicator" size="16" />
          </router-link>
        </template>
      </draggable>
    </nav>

    <div class="sidebar-footer">
      <button class="nav-item collapse-btn" style="margin-bottom: 8px;" @click="toggleLightMode">
        <Sun v-if="isLightMode" class="nav-icon" size="20" />
        <Moon v-else class="nav-icon" size="20" />
        <span>{{ isLightMode ? $t('sidebar.darkMode') : $t('sidebar.lightMode') }}</span>
      </button>
      <button class="nav-item collapse-btn" style="margin-bottom: 8px;" @click="toggleLanguage">
        <GlobeLock class="nav-icon" size="20" />
        <span>{{ locale === 'en' ? $t('sidebar.languageFrench') : $t('sidebar.languageEnglish') }}</span>
      </button>
      <router-link to="/settings" :class="['nav-item', { active: route.path === '/settings' }]">
        <Settings class="nav-icon" size="20" />
        <span>{{ $t('sidebar.settings') }}</span>
      </router-link>
    </div>
  </aside>

  <!-- Main Content -->
  <main class="main-content" :class="{ 'sidebar-closed': !isSidebarVisible }">
    <button v-if="!isSidebarVisible" class="floating-sidebar-toggle" @click="isSidebarVisible = true" :title="$t('sidebar.showSidebar')">
      <Menu size="20" />
    </button>

    <!-- Router View for Pages -->
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </main>
</template>

<style scoped>
/* Typography & Colors */
.text-orange { color: var(--accent-orange); }
.text-purple { color: var(--accent-purple); }
.text-red { color: var(--accent-red); }
.text-green { color: var(--accent-green); }
.text-muted { color: var(--text-muted); }

.bg-orange-dim { background: rgba(var(--accent-rgb), 0.1); }
.bg-purple-dim { background: rgba(176, 38, 255, 0.1); }
.bg-red-dim { background: rgba(255, 0, 60, 0.1); }
.bg-green-dim { background: rgba(0, 255, 136, 0.1); }

/* Sidebar */
.sidebar {
  width: 280px;
  height: calc(100vh - 32px);
  margin: 16px;
  display: flex;
  flex-direction: column;

  z-index: 10;
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 32px 24px;
  border-bottom: 1px solid var(--border-color);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: rgba(var(--accent-rgb), 0.1);
  border: 1px solid rgba(var(--accent-rgb), 0.3);

  display: flex;
  align-items: center;
  justify-content: center;

}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--text-main);
}

.brand-subtitle {
  font-size: 0.65rem;
  color: var(--accent-orange);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.pinned-menu-header {
  padding: 24px 16px 8px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
}

.nav-menu {
  padding: 8px 16px 24px 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.nav-items-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ghost-nav-item {
  opacity: 0.3;
  background: var(--overlay-10);
  border: 1px dashed var(--accent-orange);

}

.nav-section {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
  padding-left: 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;

  text-decoration: none;
  color: var(--text-muted);
  transition: var(--transition);
  position: relative;
}

.nav-item:hover {
  background: var(--overlay-10);
  color: var(--text-main);
}

.nav-item.active {
  background: rgba(var(--accent-rgb), 0.1);
  color: var(--accent-orange);
  border: 1px solid rgba(var(--accent-rgb), 0.2);
}

.active-indicator {
  margin-left: auto;
}

.sidebar-footer {
  padding: 24px 16px;
  border-top: 1px solid var(--border-color);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 16px 16px 0;
  overflow: hidden;
  transition: padding 0.3s ease;
}

.main-content.sidebar-closed {
  padding-left: 64px;
}

.floating-sidebar-toggle {
  position: absolute;
  top: 16px;
  left: 16px;
  background: var(--bg-panel);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 8px;

  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: var(--transition);
}
.floating-sidebar-toggle:hover {
  background: rgba(var(--accent-rgb), 0.2);
  color: var(--accent-orange);
  border-color: var(--accent-orange);
}

.collapse-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  width: 100%;
  margin-bottom: 8px;
}
.collapse-btn:hover {
  background: var(--overlay-10);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    margin: 0;
    height: 100%;
    z-index: 999;
    background: var(--bg-panel);
    box-shadow: 4px 0 20px rgba(0,0,0,0.5);
  }
  .main-content {
    padding: 16px;
    padding-top: 60px; /* Space for the floating button */
  }
  .main-content.sidebar-closed {
    padding-left: 16px;
  }
  .floating-sidebar-toggle {
    top: 10px;
    left: 10px;
    position: fixed;
    z-index: 900;
  }
}
</style>
