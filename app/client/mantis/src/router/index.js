import { createRouter, createWebHashHistory } from 'vue-router'
import ProjectsView from '../views/ProjectsView.vue'
import ResourceItemsForm from '@/views/ResourceItemsForm.vue'
import SheetProjectForm from '@/views/SheetProjectForm.vue'
import ChainCustodyView from '@/views/ChainCustodyView.vue'
import CustodyChainForm from '@/views/CustodyChainForm.vue'

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
      path: '/sheet/view/:id',
      name: 'sheet-view',
      component: ChainCustodyView,
    },
    {
      path: '/custody/form',
      name: 'custody-form',
      component: CustodyChainForm,
    }
  ]
})

export default router
