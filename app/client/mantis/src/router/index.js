import { createRouter, createWebHashHistory } from 'vue-router'
import ProjectsView from '../views/projects/ProjectsView.vue'
import ResourceItemsForm from '@/views/projects/ResourceItemsForm.vue'
import CustodyChainView from '@/views/chain_custody/CustodyChainView.vue'
import CustodyChainForm from '@/views/chain_custody/CustodyChainForm.vue'
import SheetProjectView from '@/views/sheet_projects/SheetProjectView.vue'
import SheetProjectForm from '@/views/sheet_projects/SheetProjectForm.vue'
import ShippingGuideView from '@/views/shipping_guides/ShippingGuideView.vue'
import ShippingGuideForm from '@/views/shipping_guides/ShippingGuideForm.vue'
import MaintenanceSheetForm from '@/views/maintenance_sheets/MaintenanceSheetForm.vue'

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
      path: '/custody-chain/form/:id?',
      name: 'custody-chain-form',
      component: CustodyChainForm,
    },
    {
      path: '/work-sheet/:id/',
      name: 'sheet-project-view',
      component: SheetProjectView,
    },
    {
      path: '/work-sheet/form/:id?',
      name: 'sheet-project-form',
      component: SheetProjectForm,
    },
    {
      path: '/shipping-guides',
      name: 'shipping-guide-list',
      component: ShippingGuideView,
    },
    {
      path: '/shipping-guides/form/:id?',
      name: 'shipping-guide-form',
      component: ShippingGuideForm,
    },
    {
      path: '/maintenance-sheets/form/:id?',
      name: 'maintenance-sheet-form',
      component: MaintenanceSheetForm,
    },
  ]
})

export default router
