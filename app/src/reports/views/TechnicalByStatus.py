from django.views.generic import TemplateView
from accounts.models import Technical, PassTechnical, VaccinationRecord
from common.TechnicalIssuesCheck import TechnicalIssuesCheck
from common.TechnicalPassIssuesCheck import TechnicalPassIssuesCheck
from common.TechnicalVaccinesIssuesCheck import TechnicalVaccinesIssuesCheck
from common.AppLoggin import loggin_event


class TechnicalByStatusView(TemplateView):
    template_name = "reports/technicals_status_report.html"

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte de técnicos por estado")
        context = super().get_context_data(**kwargs)

        # Obtener todos los técnicos activos
        all_technicals = Technical.objects.filter(is_active=True)

        # Lista para todos los técnicos con su estado
        all_technicals_list = []
        
        # Contadores
        stats = {
            'total': 0,
            'sin_alertas': 0,
            'alertas_vencidas': 0,
            'alertas_10_dias': 0,
            'alertas_30_dias': 0,
            'sin_pases': 0,
            'sin_vacunas': 0,
        }

        # Analizar cada técnico
        for technical in all_technicals:
            # Obtener alertas de certificados/documentos
            cert_issues = TechnicalIssuesCheck.issues_for(technical)
            
            # Obtener alertas de pases
            passes = PassTechnical.objects.filter(technical=technical, is_active=True)
            pass_issues = []
            for pass_record in passes:
                pass_issues.extend(TechnicalPassIssuesCheck.issues_for(pass_record))
            
            # Obtener alertas de vacunas
            vaccine_issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
            
            # Consolidar todas las alertas
            all_issues = cert_issues + pass_issues + vaccine_issues
            
            # Clasificar alertas por severidad
            expired_issues = [i for i in all_issues if i['status'] == 'expired']
            due_10_issues = [i for i in all_issues if i['status'] == 'due_10']
            due_30_issues = [i for i in all_issues if i['status'] == 'due_30']
            
            # Determinar el estado general del técnico
            if expired_issues:
                status_display = 'CON VENCIDOS'
                status_class = 'danger'
                stats['alertas_vencidas'] += 1
            elif due_10_issues:
                status_display = 'URGENTE (≤10 días)'
                status_class = 'warning'
                stats['alertas_10_dias'] += 1
            elif due_30_issues:
                status_display = 'PRÓXIMO (≤30 días)'
                status_class = 'info'
                stats['alertas_30_dias'] += 1
            else:
                status_display = 'AL DÍA'
                status_class = 'success'
                stats['sin_alertas'] += 1
            
            # Verificar si tiene pases
            has_passes = passes.exists()
            if not has_passes:
                stats['sin_pases'] += 1
            
            # Verificar si tiene vacunas
            has_vaccines = VaccinationRecord.objects.filter(
                technical=technical, is_active=True
            ).exists()
            if not has_vaccines:
                stats['sin_vacunas'] += 1
            
            stats['total'] += 1
            
            # Preparar datos del técnico
            technical_data = {
                'technical': technical,
                'status_display': status_display,
                'status_class': status_class,
                'all_issues': all_issues,
                'expired_count': len(expired_issues),
                'due_10_count': len(due_10_issues),
                'due_30_count': len(due_30_issues),
                'total_issues': len(all_issues),
                'has_passes': has_passes,
                'has_vaccines': has_vaccines,
                'passes_count': passes.count(),
                'work_area': technical.get_work_area_display(),
            }
            
            all_technicals_list.append(technical_data)

        # Ordenar por estado (con alertas primero)
        all_technicals_list.sort(
            key=lambda x: (
                0 if x['expired_count'] > 0 else 
                1 if x['due_10_count'] > 0 else 
                2 if x['due_30_count'] > 0 else 3,
                x['technical'].last_name
            )
        )

        context.update({
            'all_technicals': all_technicals_list,
            'stats': stats,
        })

        return context
