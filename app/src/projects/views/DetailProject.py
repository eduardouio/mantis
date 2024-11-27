from django.views.generic import DetailView
from django.core.serializers import serialize
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project, ProjectResourceItem, WorkOrder
from equipment.models import ResourceItem


class DetailProject(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'presentations/project_presentation.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        free_equipment = ResourceItem.get_free_equipment()
        project_equipment = ProjectResourceItem.get_project_equipment(
            self.object
        )
        work_orders = WorkOrder.get_by_project(self.object)
        context['title_section'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )

        context['title_page'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        context['free_equipment'] = serialize('json', free_equipment)
        context['project_resource'] = []
        context['project_json'] = serialize('json', [self.object])
        context['project'] = self.object
        context['work_orders'] = work_orders

        for i in project_equipment:
            context['project_resource'].append({
                'project_resource': serialize('json', [i]),
                'resourse_item':  serialize('json', [i.resource_item])
            })

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        message = ''
        if context['action'] == 'created':
            message = 'El proyecto ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El proyecto ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el proyecto. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context

