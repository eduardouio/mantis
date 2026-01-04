from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from accounts.models.Technical import Technical
from accounts.models.PassTechnical import PassTechnical
from accounts.models.VaccinationRecord import VaccinationRecord


class TechnicalInformationReport(TemplateView):
	template_name = 'reports/technical_report.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		technical_id = self.kwargs.get('id')
		
		technical = get_object_or_404(Technical, id=technical_id)
		pass_technical = PassTechnical.objects.filter(technical_id=technical_id, is_active=True).first()
		vaccination_records = VaccinationRecord.get_all_by_technical(technical_id)

		context['technical'] = technical
		context['pass_technical'] = pass_technical
		context['vaccination_records'] = vaccination_records
		# Agregar información del usuario de forma segura
		context['report_generated_by'] = (
			self.request.user.get_full_name() 
			if self.request.user.is_authenticated 
			else 'Sistema'
		)
		
		return context