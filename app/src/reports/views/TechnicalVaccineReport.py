from django.views.generic import TemplateView
from accounts.models.Technical import Technical
from accounts.models.VaccinationRecord import VaccinationRecord



class TechnicalVaccineReport(TemplateView):
	template_name = 'reports/technical_vaccine_report.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		technical_id = self.kwargs.get('id')
		
		technical = Technical.objects.get(id=technical_id)
		vaccination_records = VaccinationRecord.get_all_by_technical(technical_id)

		context['technical'] = technical
		context['vaccination_records'] = vaccination_records
		
		return context