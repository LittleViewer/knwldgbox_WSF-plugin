import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Monitoring from '../views/Monitoring.vue'
import Settings from '../views/Settings.vue'
import SocialForensics from '../views/SocialForensics.vue'
import TargetAnalysis from '../views/TargetAnalysis.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/monitoring',
      name: 'monitoring',
      component: Monitoring
    },
    {
      path: '/social',
      name: 'social-forensics',
      component: SocialForensics
    },
    {
      path: '/target',
      name: 'target-analysis',
      component: TargetAnalysis
    },
    {
      path: '/network',
      name: 'network-graph',
      component: () => import('../views/NetworkGraph.vue')
    },
    {
      path: '/leaks',
      name: 'data-leaks',
      component: () => import('../views/DataLeaks.vue')
    },
    {
      path: '/tools',
      name: 'knwldg-tools',
      component: () => import('../views/KnwldgTools.vue')
    },
    {
      path: '/downloaders',
      name: 'media-downloaders',
      component: () => import('../views/MediaDownloaders.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
    },
    {
      path: '/archives',
      name: 'archives',
      component: () => import('../views/Archives.vue')
    },
    {
      path: '/osint-map',
      name: 'osint-map',
      component: () => import('../views/OsintMap.vue')
    },
    {
      path: '/dorks',
      name: 'dork-builder',
      component: () => import('../views/DorkBuilder.vue')
    },
    {
      path: '/image-forensics',
      name: 'image-forensics',
      component: () => import('../views/ImageForensics.vue')
    },
    {
      path: '/ai-chat',
      name: 'ai-chat',
      component: () => import('../views/AIChatbot.vue')
    }
  ]
})

export default router
