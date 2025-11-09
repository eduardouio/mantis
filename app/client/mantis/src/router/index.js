import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '../views/ProjectsView.vue'
import ResourceItemsForm from '@/views/ResourceItemsForm.vue'
import SheetProjectForm from '@/views/SheetProjectForm.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
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
  ],
})
  
export default router
