from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from accounts.models import Technical, PassTechnical, VaccinationRecord
from datetime import date, timedelta


class TechnicalDetailView(LoginRequiredMixin, DetailView):
    model = Technical
    template_name = 'presentations/technical_presentation.html'
    context_object_name = 'technical'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Ficha de Técnico'
        context['title_section'] = 'Ficha de Técnico'
        context['action'] = self.request.GET.get('action', None)
        
        # Agregar fecha de hoy para comparaciones en la plantilla
        context['today'] = date.today()

        # Obtener registros de vacunación
        vaccination_records = VaccinationRecord.get_all_by_technical(
            technical_id=self.object.id
        )
        
        # Enriquecer datos de vacunación con estado de completitud
        for record in vaccination_records:
            record.is_complete = self._is_vaccination_complete(record)
        
        context['vaccination_records'] = vaccination_records

        # Obtener todos los pases técnicos asociados al técnico
        pass_technical = PassTechnical.objects.filter(technical=self.object)
        
        # Enriquecer pases con información de expiración
        for pass_item in pass_technical:
            pass_item.expiry_status = self._get_expiry_status(pass_item.fecha_caducidad)
        
        context['pass_technical'] = pass_technical

        # Información de expiración de certificados
        context['license_expiry_details'] = self._get_expiry_status(self.object.license_expiry_date)
        context['defensive_driving_expiry_details'] = self._get_expiry_status(self.object.defensive_driving_certificate_expiry_date)
        context['mae_expiry_details'] = self._get_expiry_status(self.object.mae_certificate_expiry_date)
        context['medical_expiry_details'] = self._get_expiry_status(self.object.medical_certificate_expiry_date)
        
        # Información Quest con estado de expiración
        if self.object.quest_end_date:
            context['quest_end_details'] = self._get_expiry_status(self.object.quest_end_date)

        # Estadísticas para metadatos
        context['expired_certificates_count'] = self._count_expired_certificates()
        context['expiring_certificates_count'] = self._count_expiring_certificates(days=30)
        context['complete_vaccinations_count'] = sum(1 for rec in vaccination_records if self._is_vaccination_complete(rec))

        return context

    def _get_expiry_status(self, expiry_date):
        """Calcula el estado de expiración de una fecha dada"""
        if not expiry_date:
            return None
            
        today = date.today()
        days_remaining = (expiry_date - today).days
        
        if days_remaining < 0:
            return {
                'days_remaining': abs(days_remaining),
                'text': f'Vencido hace {abs(days_remaining)} días',
                'class': 'text-red-600 font-semibold'
            }
        elif days_remaining <= 15:
            return {
                'days_remaining': days_remaining,
                'text': f'Vence en {days_remaining} días',
                'class': 'text-orange-600 font-semibold'
            }
        elif days_remaining <= 30:
            return {
                'days_remaining': days_remaining,
                'text': f'Vence en {days_remaining} días',
                'class': 'text-yellow-600'
            }
        else:
            return {
                'days_remaining': days_remaining,
                'text': f'Vigente por {days_remaining} días',
                'class': 'text-green-600'
            }

    def _is_vaccination_complete(self, vaccination_record):
        """Determina si un registro de vacunación está completo"""
        # Verificar si tiene fecha de aplicación (básico para considerar que se inició)
        if not vaccination_record.application_date:
            return False
            
        # Criterio específico por tipo de vacuna
        if hasattr(vaccination_record, 'vaccine_type'):
            if vaccination_record.vaccine_type == 'COVID19':
                # Para COVID-19, verificar si tiene próxima dosis programada o ya pasó tiempo suficiente
                return vaccination_record.next_dose_date is None or vaccination_record.next_dose_date < date.today()
            elif vaccination_record.vaccine_type == 'HEPATITIS_B':
                # Para Hepatitis B, verificar si completó el esquema (usualmente 3 dosis)
                return vaccination_record.next_dose_date is None or vaccination_record.next_dose_date < date.today()
            elif vaccination_record.vaccine_type == 'INFLUENZA':
                # Influenza es anual, verificar si la aplicación fue este año
                if vaccination_record.application_date:
                    return vaccination_record.application_date.year == date.today().year
            elif vaccination_record.vaccine_type == 'TETANUS':
                # Tétanos dura varios años, verificar si la aplicación fue reciente
                if vaccination_record.application_date:
                    years_since_application = (date.today() - vaccination_record.application_date).days / 365
                    return years_since_application < 10  # Tétanos dura ~10 años
        
        # Default: si tiene fecha de aplicación y no hay próxima dosis pendiente
        return vaccination_record.application_date is not None and (
            vaccination_record.next_dose_date is None or 
            vaccination_record.next_dose_date < date.today()
        )

    def _count_expired_certificates(self):
        """Cuenta certificados vencidos"""
        today = date.today()
        expired_count = 0
        
        certificates = [
            self.object.license_expiry_date,
            self.object.defensive_driving_certificate_expiry_date,
            self.object.mae_certificate_expiry_date,
            self.object.medical_certificate_expiry_date
        ]
        
        for cert_date in certificates:
            if cert_date and cert_date < today:
                expired_count += 1
                
        return expired_count

    def _count_expiring_certificates(self, days=30):
        """Cuenta certificados que vencen en los próximos N días"""
        today = date.today()
        expiring_date = today + timedelta(days=days)
        expiring_count = 0
        
        certificates = [
            self.object.license_expiry_date,
            self.object.defensive_driving_certificate_expiry_date,
            self.object.mae_certificate_expiry_date,
            self.object.medical_certificate_expiry_date
        ]
        
        for cert_date in certificates:
            if cert_date and today <= cert_date <= expiring_date:
                expiring_count += 1
                
        return expiring_count
