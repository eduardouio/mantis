from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from accounts.models.Technical import Technical
from accounts.models.PassTechnical import PassTechnical
from accounts.models.VaccinationRecord import VaccinationRecord
from common.TechnicalIssuesCheck import TechnicalIssuesCheck


class TechnicalInformationReport(TemplateView):
	template_name = 'reports/technical_report.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		technical_id = self.kwargs.get('id')
		
		technical = get_object_or_404(Technical, id=technical_id)
		
		# Certificados con evaluación de estado
		certificates = [
			{
				'label': 'Licencia de Conducir',
				'issue_date': technical.license_issue_date,
				'expiry_date': technical.license_expiry_date,
			},
			{
				'label': 'Manejo Defensivo',
				'issue_date': technical.defensive_driving_certificate_issue_date,
				'expiry_date': technical.defensive_driving_certificate_expiry_date,
			},
			{
				'label': 'Certificado MAE',
				'issue_date': technical.mae_certificate_issue_date,
				'expiry_date': technical.mae_certificate_expiry_date,
			},
			{
				'label': 'Certificado Médico',
				'issue_date': technical.medical_certificate_issue_date,
				'expiry_date': technical.medical_certificate_expiry_date,
			},
		]

		# Evaluar estado de cada certificado
		for cert in certificates:
			if cert['expiry_date']:
				status, days_left = TechnicalIssuesCheck._evaluate(cert['expiry_date'])
				cert['status'] = status
				cert['days_left'] = days_left
				if status == 'expired':
					cert['status_class'] = 'status-expired'
					cert['status_text'] = f'VENCIDO ({abs(days_left)} días)'
				elif status == 'due_10':
					cert['status_class'] = 'status-due-10'
					cert['status_text'] = f'POR VENCER ({days_left} días)'
				elif status == 'due_30':
					cert['status_class'] = 'status-due-30'
					cert['status_text'] = f'PRÓXIMO A VENCER ({days_left} días)'
				else:
					cert['status_class'] = 'status-valid'
					cert['status_text'] = f'VIGENTE ({days_left} días)'
			else:
				cert['status_class'] = 'status-na'
				cert['status_text'] = 'NO REGISTRADO'

		context['certificates'] = certificates

		# Pases del técnico
		passes = PassTechnical.objects.filter(technical_id=technical_id, is_active=True)
		passes_data = []
		for p in passes:
			pass_data = {
				'bloque': p.bloque,
				'fecha_caducidad': p.fecha_caducidad.strftime('%d/%m/%Y') if p.fecha_caducidad else 'N/A',
			}
			if p.fecha_caducidad:
				status, days_left = TechnicalIssuesCheck._evaluate(p.fecha_caducidad)
				if status == 'expired':
					pass_data['status_class'] = 'status-expired'
					pass_data['status_text'] = 'VENCIDO'
				elif status in ['due_10', 'due_30']:
					pass_data['status_class'] = 'status-due-10'
					pass_data['status_text'] = f'POR VENCER ({days_left} días)'
				else:
					pass_data['status_class'] = 'status-valid'
					pass_data['status_text'] = 'VIGENTE'
			else:
				pass_data['status_class'] = 'status-na'
				pass_data['status_text'] = 'SIN FECHA'
			passes_data.append(pass_data)

		context['passes'] = passes_data

		# Vacunas con evaluación
		vaccination_records = VaccinationRecord.get_all_by_technical(technical_id)
		vaccines_data = []
		for vaccine in vaccination_records:
			vaccine_data = {
				'type': vaccine.get_vaccine_type_display(),
				'application_date': vaccine.application_date.strftime('%d/%m/%Y') if vaccine.application_date else 'N/A',
				'next_dose_date': vaccine.next_dose_date.strftime('%d/%m/%Y') if vaccine.next_dose_date else 'N/A',
				'batch_number': vaccine.batch_number or 'N/A',
				'dose_number': vaccine.dose_number or 'N/A',
			}
			if vaccine.next_dose_date:
				status, days_left = TechnicalIssuesCheck._evaluate(vaccine.next_dose_date)
				if status == 'expired':
					vaccine_data['status_class'] = 'status-expired'
					vaccine_data['status_text'] = 'ATRASADA'
				elif status in ['due_10', 'due_30']:
					vaccine_data['status_class'] = 'status-due-10'
					vaccine_data['status_text'] = f'PRÓXIMA ({days_left} días)'
				else:
					vaccine_data['status_class'] = 'status-valid'
					vaccine_data['status_text'] = 'AL DÍA'
			else:
				vaccine_data['status_class'] = 'status-na'
				vaccine_data['status_text'] = 'COMPLETA'
			vaccines_data.append(vaccine_data)

		context['vaccines'] = vaccines_data
		context['technical'] = technical
		context['report_generated_by'] = (
			self.request.user.get_full_name() 
			if self.request.user.is_authenticated 
			else 'Sistema'
		)
		
		return context