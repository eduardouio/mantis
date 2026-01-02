from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.TechnicalIssuesCheck import TechnicalIssuesCheck
from common.TechnicalPassIssuesCheck import TechnicalPassIssuesCheck
from common.TechnicalVaccinesIssuesCheck import TechnicalVaccinesIssuesCheck
from common.VehicleIssuesCheck import VehicleIssuesCheck
from common.VehichlePassIssuesCheck import PassVehichleIssuesCheck
from common.VehicleIssuesCertificationVehicle import VehicleIssuesCertificationVehicle


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

        return context
