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
    {'type': 'HEPATITIS_A', 'name': 'Hepatitis A', 'max_doses': 3},
    {'type': 'HEPATITIS_B', 'name': 'Hepatitis B', 'max_doses': 3},
    {'type': 'INFLUENZA', 'name': 'Influenza estacional', 'max_doses': 2},
    {'type': 'YELLOW_FEVER', 'name': 'Fiebre Amarilla', 'max_doses': 2},
    {'type': 'MEASLES', 'name': 'Sarampión/Rubéola', 'max_doses': 1},
    {'type': 'TYPHOID', 'name': 'Tifoidea', 'max_doses': 5},
    {'type': 'COVID', 'name': 'COVID 19', 'max_doses': 5},
    {'type': 'OTHER1', 'name': ' ', 'max_doses': 5},
	{'type': 'OTHER2', 'name': ' ', 'max_doses': 5},
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
		# Partes de nombres y apellidos
		context['first_name_split'] = self._split_name_parts(technical.first_name)
		context['last_name_split'] = self._split_name_parts(technical.last_name)
		# Agregar información del usuario de forma segura
		context['report_generated_by'] = (
			self.request.user.get_full_name() 
			if self.request.user.is_authenticated 
			else 'Sistema'
		)
		
		return context

	def _organize_vaccines(self, records):
		"""
		Organiza los registros de vacunación según las definiciones de vacunas.
		"""
		organized = []
		hep_ab_records = [r for r in records if r.vaccine_type == 'HEPATITIS_A_B']
		other_records = [r for r in records if r.vaccine_type == 'OTHER']

		for vaccine_def in VACCINE_DEFINITIONS:
			vtype = vaccine_def['type']

			# Selección de registros según el tipo
			if vtype == 'HEPATITIS_A':
				vaccine_records = [r for r in records if r.vaccine_type == 'HEPATITIS_A']
				if not vaccine_records:
					vaccine_records = self._consume_records(hep_ab_records, vaccine_def['max_doses'])
			elif vtype == 'HEPATITIS_B':
				vaccine_records = [r for r in records if r.vaccine_type == 'HEPATITIS_B']
				if not vaccine_records:
					vaccine_records = self._consume_records(hep_ab_records, vaccine_def['max_doses'])
			elif vtype in ('OTHER1', 'OTHER2'):
				vaccine_records = self._consume_records(other_records, vaccine_def['max_doses'])
			else:
				vaccine_records = [r for r in records if r.vaccine_type == vtype]

			doses = []
			for dose_num in range(1, vaccine_def['max_doses'] + 1):
				dose_record = next(
					(r for r in vaccine_records if r.dose_number == dose_num),
					vaccine_records[dose_num - 1] if dose_num - 1 < len(vaccine_records) else None
				)
				doses.append({'number': dose_num, 'record': dose_record})

			has_records = any(d['record'] for d in doses)
			organized.append({
				'name': vaccine_def['name'],
				'type': vtype,
				'max_doses': vaccine_def['max_doses'],
				'doses': doses,
				'has_records': has_records
			})

		return organized

	def _consume_records(self, record_list, max_items):
		"""
		Extrae hasta max_items registros de la lista dada y los remueve de ella.
		"""
		consumed = record_list[:max_items]
		del record_list[:max_items]
		return consumed

	def _split_name_parts(self, full_name):
		"""
		Retorna una tupla (primero, segundo) a partir de un nombre completo.
		"""
		if not full_name:
			return ("", "")
		parts = full_name.strip().split()
		first = parts[0] if parts else ""
		second = " ".join(parts[1:]) if len(parts) > 1 else ""
		return (first, second)