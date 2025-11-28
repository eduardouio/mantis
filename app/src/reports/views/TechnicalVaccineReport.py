from django.views.generic import TemplateView
from accounts.models.Technical import Technical
from accounts.models.VaccinationRecord import VaccinationRecord


# Configuración de la empresa
COMPANY_INFO = {
    'name': 'PEISOL S.A',
    'ruc': '2191744791001',
}

# Definición de vacunas con sus dosis máximas
VACCINE_DEFINITIONS = [
    {'type': 'TETANUS', 'name': 'Tétanos - Difteria', 'max_doses': 5},
    {'type': 'HEPATITIS_A_B', 'name': 'Hepatitis A y B', 'max_doses': 3},
    {'type': 'INFLUENZA', 'name': 'Influenza estacional', 'max_doses': 2},
    {'type': 'YELLOW_FEVER', 'name': 'Fiebre Amarilla', 'max_doses': 2},
    {'type': 'MEASLES', 'name': 'Sarampión/Rubéola', 'max_doses': 1},
    {'type': 'TYPHOID', 'name': 'Tifoidea', 'max_doses': 1},
    {'type': 'COVID', 'name': 'COVID 19', 'max_doses': 5},
    {'type': 'OTHER', 'name': 'Otra', 'max_doses': 3},
]


class TechnicalVaccineReport(TemplateView):
	template_name = 'reports/technical_vaccine_report.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		technical_id = self.kwargs.get('id')
		
		technical = Technical.objects.get(id=technical_id)
		vaccination_records = list(VaccinationRecord.get_all_by_technical(technical_id))

		# Organizar vacunas según definiciones
		vaccines_data = self._organize_vaccines(vaccination_records)

		context['technical'] = technical
		context['company_info'] = COMPANY_INFO
		context['vaccines'] = vaccines_data
		
		return context

	def _organize_vaccines(self, records):
		"""
		Organiza los registros de vacunación según las definiciones de vacunas.
		"""
		organized = []
		
		for vaccine_def in VACCINE_DEFINITIONS:
			vaccine_records = [r for r in records if r.vaccine_type == vaccine_def['type']]
			doses = []
			
			for dose_num in range(1, vaccine_def['max_doses'] + 1):
				dose_record = next(
					(r for r in vaccine_records if r.dose_number == dose_num), 
					None
				)
				doses.append({
					'number': dose_num,
					'record': dose_record
				})
			
			# Solo agregar si tiene al menos un registro
			has_records = any(d['record'] for d in doses)
			
			organized.append({
				'name': vaccine_def['name'],
				'type': vaccine_def['type'],
				'max_doses': vaccine_def['max_doses'],
				'doses': doses,
				'has_records': has_records
			})
		
		return organized