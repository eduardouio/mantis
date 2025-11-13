import { createRouter, createWebHashHistory } from 'vue-router'
import ProjectsView from '../views/projects/ProjectsView.vue'
import ResourceItemsForm from '@/views/projects/ResourceItemsForm.vue'
import SheetProjectForm from '@/views/projects/SheetProjectForm.vue'
import ChainCustodyView from '@/views/chain_custody/ChainCustodyView.vue'
import ChainCustodyForm from '@/views/chain_custody/ChainCustodyForm.vue'

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
      path: '/sheet/form',
      name: 'sheet-form',
      component: SheetProjectForm,
    },
    {
      path: '/chain-custody',
      name: 'chain-custody',
      component: ChainCustodyView,
    },
    {
      path: '/chain-custody/form',
      name: 'chain-custody-form',
      component: ChainCustodyForm,
    },
  ]
})

export default router
