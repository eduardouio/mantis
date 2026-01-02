from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.TechnicalIssuesCheck import TechnicalIssuesCheck
from common.TechnicalPassIssuesCheck import TechnicalPassIssuesCheck
from common.TechnicalVaccinesIssuesCheck import TechnicalVaccinesIssuesCheck
from common.VehicleIssuesCheck import VehicleIssuesCheck
from common.VehichlePassIssuesCheck import PassVehichleIssuesCheck
from common.VehicleIssuesCertificationVehicle import VehicleIssuesCertificationVehicle
from common.StatusResourceItem import StatusResourceItem
from equipment.models import ResourceItem


class HomeTV(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user

        all_issues = []

        all_issues.extend(TechnicalIssuesCheck.issues_all())
        all_issues.extend(TechnicalPassIssuesCheck.issues_all())
        all_issues.extend(TechnicalVaccinesIssuesCheck.issues_all())

        all_issues.extend(VehicleIssuesCheck.issues_all())
        all_issues.extend(PassVehichleIssuesCheck.issues_all())
        all_issues.extend(VehicleIssuesCertificationVehicle.issues_all())

        # Añadir días_vencido_abs para valores negativos
        for issue in all_issues:
            if issue['days_left'] < 0:
                issue['days_expired_abs'] = abs(issue['days_left'])

        expired = [i for i in all_issues if i["status"] == "expired"]
        due_10 = [i for i in all_issues if i["status"] == "due_10"]
        due_30 = [i for i in all_issues if i["status"] == "due_30"]

        technical_issues = [i for i in all_issues if "technical_id" in i]
        vehicle_issues = [i for i in all_issues if "vehicle_id" in i]

        context["alerts"] = {
            "all": all_issues,
            "expired": expired,
            "due_10": due_10,
            "due_30": due_30,
            "technical": technical_issues,
            "vehicle": vehicle_issues,
            "total": len(all_issues),
            "total_expired": len(expired),
            "total_due_10": len(due_10),
            "total_due_30": len(due_30),
        }

        # Análisis de recursos (solo equipos, no servicios)
        equipments = ResourceItem.objects.filter(
            is_active=True,
            is_deleted=False,
            type_equipment__isnull=False
        ).exclude(
            type_equipment='SERVIC'  # Excluir servicios
        )
        
        equipment_status = []
        incomplete_equipments = []
        rented_equipments = []
        available_equipments = []
        equipments_with_issues = []
        
        for equipment in equipments:
            analyzer = StatusResourceItem(equipment)
            report = analyzer.get_status_report()
            
            status_info = {
                'equipment': equipment,
                'report': report,
                'completion_percentage': report['completeness']['completion_percentage'],
                'is_complete': report['completeness']['is_complete'],
                'availability_status': report['availability']['status'],
                'has_issues': len(report['inconsistencies']['found']) > 0,
                'missing_count': len(report['completeness']['missing_items']),
            }
            
            equipment_status.append(status_info)
            
            if not status_info['is_complete']:
                incomplete_equipments.append(status_info)
            
            if status_info['availability_status'] == 'RENTADO':
                rented_equipments.append(status_info)
            elif status_info['availability_status'] == 'DISPONIBLE':
                available_equipments.append(status_info)
            
            if status_info['has_issues']:
                equipments_with_issues.append(status_info)
        
        context["equipment_status"] = {
            'all': equipment_status,
            'incomplete': incomplete_equipments,
            'rented': rented_equipments,
            'available': available_equipments,
            'with_issues': equipments_with_issues,
            'total': len(equipment_status),
            'total_incomplete': len(incomplete_equipments),
            'total_rented': len(rented_equipments),
            'total_available': len(available_equipments),
            'total_with_issues': len(equipments_with_issues),
        }

        return context
