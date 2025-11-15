import { createRouter, createWebHashHistory } from 'vue-router'
import ProjectsView from '../views/projects/ProjectsView.vue'
import ResourceItemsForm from '@/views/projects/ResourceItemsForm.vue'
import CustodyChainView from '@/views/chain_custody/CustodyChainView.vue'
import CustodyChainForm from '@/views/chain_custody/CustodyChainForm.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/project'
    },
    {
      path: '/project',
      name: 'projects-detail',
      component: ProjectsView,
    },
    {
      path: '/resource/form',
      name: 'resource-form',
      component: ResourceItemsForm,
    },
    {
      path: '/custody-chain',
      name: 'custody-chain',
      component: CustodyChainView,
    },
    {
      path: '/custody-chain/form',
      name: 'custody-chain-form',
      component: CustodyChainForm,
    },
  ]
})

export default router
