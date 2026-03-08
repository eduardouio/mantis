from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Subquery, OuterRef
from projects.models import Project
from projects.models.SheetProject import SheetProject


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'lists/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.annotate(
            sheets_count=Count(
                'sheetproject',
                filter=Q(sheetproject__is_deleted=False),
            ),
            equipos_count=Count(
                'projectresourceitem',
                filter=Q(
                    projectresourceitem__type_resource='EQUIPO',
                    projectresourceitem__is_deleted=False,
                ),
            ),
            servicios_count=Count(
                'projectresourceitem',
                filter=Q(
                    projectresourceitem__type_resource='SERVICIO',
                    projectresourceitem__is_deleted=False,
                ),
            ),
            has_active_sheet=Count(
                'sheetproject',
                filter=Q(
                    sheetproject__status='IN_PROGRESS',
                    sheetproject__is_deleted=False,
                ),
            ),
            last_sheet_id=Subquery(
                SheetProject.objects.filter(
                    project=OuterRef('pk'),
                    is_deleted=False,
                ).order_by('-id').values('id')[:1]
            ),
        ).select_related('partner')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado De Proyectos Registrados'
        context['title_page'] = 'Listado De Proyectos'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El proyecto ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context
