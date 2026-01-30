import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Analysis from '../views/Analysis.vue'
import LocalAnalysis from '../views/LocalAnalysis.vue'
import Settings from '../views/Settings.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: Analysis
    },
    {
      path: '/local-analysis',
      name: 'localAnalysis',
      component: LocalAnalysis
    },
    {
      path: '/local-analysis/:turbineId',
      name: 'turbineDetail',
      component: LocalAnalysis
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
    }
  ]
})

export default router