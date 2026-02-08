"""
PartnerCompleteInfo - Información Completa del Partner (Cliente)

Esta clase consolida toda la información relevante de un partner/cliente:
- Datos básicos del cliente
- Proyectos asociados y su estado
- Equipos asignados a cada proyecto
- Historia de mantenimientos
- Planillas generadas (SheetProject)
- Estadísticas financieras y operativas
- Información de facturación

Uso:
    partner_info = PartnerCompleteInfo(partner_id=1)
    complete_data = partner_info.get_complete_information()
"""

from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.utils import timezone
from typing import Dict, List, Any

# Importaciones de modelos necesarios
from projects.models.Partner import Partner
from projects.models.Project import Project, ProjectResourceItem
from projects.models.SheetProject import SheetProject


class PartnerCompleteInfo:
    """Clase para obtener información completa de un partner/cliente."""

    def __init__(self, partner_id: int):
        """
        Inicializa la clase con el ID del partner.

        Args:
            partner_id (int): ID del partner del cual obtener información
        """
        self.partner_id = partner_id
        self.partner = None
        self._load_partner()

    def _load_partner(self) -> None:
        """Carga el partner desde la base de datos."""
        try:
            self.partner = Partner.objects.get(id=self.partner_id, is_deleted=False)
        except Partner.DoesNotExist:
            raise ValueError(
                f"Partner with ID {self.partner_id} not found or is deleted"
            )

    def get_complete_information(self) -> Dict[str, Any]:
        """
        Obtiene toda la información completa del partner.

        Returns:
            Dict con toda la información estructurada del partner
        """
        return {
            "partner_basic_info": self._get_partner_basic_info(),
            "projects_summary": self._get_projects_summary(),
            "projects_detail": self._get_projects_detail(),
            "equipment_assignments": self._get_equipment_assignments(),
            "financial_summary": self._get_financial_summary(),
            "sheets_summary": self._get_sheets_summary(),
            "operational_statistics": self._get_operational_statistics(),
            "maintenance_alerts": self._get_maintenance_alerts(),
            "recent_activity": self._get_recent_activity(),
        }

    def _get_partner_basic_info(self) -> Dict[str, Any]:
        """Información básica del partner."""
        return {
            "id": self.partner.id,
            "name": self.partner.name,
            "business_tax_id": self.partner.business_tax_id,
            "email": self.partner.email,
            "phone": self.partner.phone,
            "address": self.partner.address,
            "name_contact": self.partner.name_contact,
            "notes": self.partner.notes,
            "created_at": self.partner.created_at,
            "updated_at": self.partner.updated_at,
            "is_active": self.partner.is_active,
        }

    def _get_projects_summary(self) -> Dict[str, Any]:
        """Resumen de proyectos del partner."""
        projects = Project.objects.filter(partner=self.partner, is_deleted=False)

        total_projects = projects.count()
        active_projects = projects.filter(is_closed=False).count()
        closed_projects = projects.filter(is_closed=True).count()

        # Rango de fechas de proyectos
        earliest_project = projects.order_by("start_date").first()
        latest_project = projects.order_by("-end_date").first()

        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "closed_projects": closed_projects,
            "earliest_project_date": (
                earliest_project.start_date if earliest_project else None
            ),
            "latest_project_date": (
                latest_project.end_date if latest_project else None
            ),
            "projects_duration_days": self._calculate_total_project_days(),
        }

    def _get_projects_detail(self) -> List[Dict[str, Any]]:
        """Detalle completo de cada proyecto."""
        projects = Project.objects.filter(
            partner=self.partner, is_deleted=False
        ).order_by("-start_date")

        projects_detail = []
        for project in projects:
            # Equipos asignados al proyecto
            equipment_assignments = ProjectResourceItem.objects.filter(
                project=project, is_deleted=False
            )

            # Planillas del proyecto
            sheets = SheetProject.objects.filter(project=project, is_deleted=False)

            projects_detail.append(
                {
                    "id": project.id,
                    "location": project.location,
                    "contact_name": project.contact_name,
                    "contact_phone": project.contact_phone,
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "is_closed": project.is_closed,
                    "duration_days": (
                        (project.end_date - project.start_date).days
                        if project.end_date and project.start_date
                        else None
                    ),
                    "equipment_count": equipment_assignments.count(),
                    "active_equipment": equipment_assignments.filter(
                        is_retired=False
                    ).count(),
                    "retired_equipment": equipment_assignments.filter(
                        is_retired=True
                    ).count(),
                    "sheets_count": sheets.count(),
                    "invoiced_sheets": sheets.filter(status="INVOICED").count(),
                    "total_project_value": self._calculate_project_total_value(project),
                    "created_at": project.created_at,
                    "updated_at": project.updated_at,
                }
            )

        return projects_detail

    def _get_equipment_assignments(self) -> List[Dict[str, Any]]:
        """Información detallada de equipos asignados a todos los proyectos."""
        assignments = (
            ProjectResourceItem.objects.filter(
                project__partner=self.partner,
                project__is_deleted=False,
                is_deleted=False,
            )
            .select_related("project", "resource_item")
            .order_by("-operation_start_date")
        )

        equipment_assignments = []
        for assignment in assignments:
            # Calcular días de operación
            operation_days = None
            if assignment.operation_start_date and assignment.operation_end_date:
                operation_days = (
                    assignment.operation_end_date - assignment.operation_start_date
                ).days

            # Próximo mantenimiento estimado
            next_maintenance = None
            if assignment.operation_start_date and assignment.maintenance_interval_days:
                next_maintenance = assignment.operation_start_date + timedelta(
                    days=assignment.maintenance_interval_days
                )

            equipment_assignments.append(
                {
                    "assignment_id": assignment.id,
                    "project_id": assignment.project.id,
                    "project_location": assignment.project.location,
                    "equipment_id": assignment.resource_item.id,
                    "equipment_name": assignment.resource_item.name,
                    "equipment_code": assignment.resource_item.code,
                    "equipment_type": assignment.resource_item.type_equipment,
                    "equipment_brand": assignment.resource_item.brand,
                    "equipment_model": assignment.resource_item.model,
                    "rent_cost": assignment.rent_cost,
                    "maintenance_cost": assignment.maintenance_cost,
                    "maintenance_interval_days": (assignment.maintenance_interval_days),
                    "operation_start_date": assignment.operation_start_date,
                    "operation_end_date": assignment.operation_end_date,
                    "operation_days": operation_days,
                    "is_retired": assignment.is_retired,
                    "retirement_date": assignment.retirement_date,
                    "retirement_reason": assignment.retirement_reason,
                    "next_maintenance_estimated": next_maintenance,
                    "total_assignment_value": (
                        self._calculate_assignment_total_value(assignment)
                    ),
                    "created_at": assignment.created_at,
                }
            )

        return equipment_assignments

    def _get_financial_summary(self) -> Dict[str, Any]:
        """Resumen financiero del partner."""
        assignments = ProjectResourceItem.objects.filter(
            project__partner=self.partner, project__is_deleted=False, is_deleted=False
        )

        sheets = SheetProject.objects.filter(
            project__partner=self.partner, project__is_deleted=False, is_deleted=False
        )

        # Cálculos de costos de equipos
        total_rent_cost = assignments.aggregate(total=models.Sum("rent_cost"))[
            "total"
        ] or Decimal("0.00")

        total_maintenance_cost = assignments.aggregate(
            total=models.Sum("maintenance_cost")
        )["total"] or Decimal("0.00")

        # Cálculos de planillas
        total_invoiced = sheets.filter(status="INVOICED").aggregate(
            total=models.Sum("total")
        )["total"] or Decimal("0.00")

        total_pending = sheets.filter(status="IN_PROGRESS").aggregate(
            total=models.Sum("total")
        )["total"] or Decimal("0.00")

        return {
            "total_rent_costs": total_rent_cost,
            "total_maintenance_costs": total_maintenance_cost,
            "total_equipment_costs": total_rent_cost + total_maintenance_cost,
            "total_invoiced_amount": total_invoiced,
            "total_pending_amount": total_pending,
            "total_business_value": total_invoiced + total_pending,
            "average_project_value": self._calculate_average_project_value(),
            "invoiced_sheets_count": sheets.filter(status="INVOICED").count(),
            "pending_sheets_count": sheets.filter(status="IN_PROGRESS").count(),
            "cancelled_sheets_count": sheets.filter(status="CANCELLED").count(),
        }

    def _get_sheets_summary(self) -> List[Dict[str, Any]]:
        """Resumen de todas las planillas del partner."""
        sheets = (
            SheetProject.objects.filter(
                project__partner=self.partner,
                project__is_deleted=False,
                is_deleted=False,
            )
            .select_related("project")
            .order_by("-issue_date")
        )

        sheets_summary = []
        for sheet in sheets:
            sheets_summary.append(
                {
                    "sheet_id": sheet.id,
                    "project_id": sheet.project.id,
                    "project_location": sheet.project.location,
                    "issue_date": sheet.issue_date,
                    "period_start": sheet.period_start,
                    "period_end": sheet.period_end,
                    "status": sheet.status,
                    "series_code": sheet.series_code,
                    "service_type": sheet.service_type,
                    "total_gallons": sheet.total_gallons,
                    "total_barrels": sheet.total_barrels,
                    "total_cubic_meters": sheet.total_cubic_meters,
                    "client_po_reference": sheet.client_po_reference,
                    "contact_reference": sheet.contact_reference,
                    "invoice_reference": sheet.invoice_reference,
                    "total": sheet.total,
                    "details_count": 0,  # No hay detalles disponibles
                    "created_at": sheet.created_at,
                }
            )

        return sheets_summary

    def _get_operational_statistics(self) -> Dict[str, Any]:
        """Estadísticas operativas del partner."""
        today = timezone.now().date()

        assignments = ProjectResourceItem.objects.filter(
            project__partner=self.partner, project__is_deleted=False, is_deleted=False
        )

        # Equipos actualmente en operación
        active_equipment = assignments.filter(
            operation_start_date__lte=today,
            operation_end_date__gte=today,
            is_retired=False,
        )

        # Equipos por tipo
        equipment_by_type = (
            assignments.values("resource_item__type_equipment")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )

        # Proyectos activos
        active_projects = Project.objects.filter(
            partner=self.partner, is_closed=False, is_deleted=False
        )

        return {
            "active_equipment_count": active_equipment.count(),
            "total_equipment_assigned": assignments.count(),
            "retired_equipment_count": assignments.filter(is_retired=True).count(),
            "equipment_by_type": list(equipment_by_type),
            "active_projects_count": active_projects.count(),
            "average_project_duration": (self._calculate_average_project_duration()),
            "equipment_utilization_rate": (
                self._calculate_equipment_utilization_rate()
            ),
            "most_used_equipment_type": (
                equipment_by_type.first()["resource_item__type_equipment"]
                if equipment_by_type
                else None
            ),
        }

    def _get_maintenance_alerts(self) -> List[Dict[str, Any]]:
        """Alertas de mantenimiento y fechas importantes."""
        today = timezone.now().date()
        alerts = []

        # Equipos con proyectos que terminan pronto
        assignments = ProjectResourceItem.objects.filter(
            project__partner=self.partner,
            project__is_deleted=False,
            is_deleted=False,
            is_retired=False,
            operation_end_date__gte=today,
            operation_end_date__lte=today + timedelta(days=30),
        ).select_related("project", "resource_item")

        for assignment in assignments:
            days_until_end = (assignment.operation_end_date - today).days
            if days_until_end <= 7:
                alert_level = "high"
            elif days_until_end <= 15:
                alert_level = "medium"
            else:
                alert_level = "low"

            alerts.append(
                {
                    "type": "project_ending",
                    "level": alert_level,
                    "message": (
                        f"Proyecto {assignment.project.id} termina en "
                        f"{days_until_end} días"
                    ),
                    "equipment_name": assignment.resource_item.name,
                    "project_location": assignment.project.location,
                    "end_date": assignment.operation_end_date,
                    "days_remaining": days_until_end,
                }
            )

        # Mantenimientos próximos (estimado)
        maintenance_assignments = ProjectResourceItem.objects.filter(
            project__partner=self.partner,
            project__is_deleted=False,
            is_deleted=False,
            is_retired=False,
        ).select_related("project", "resource_item")

        for assignment in maintenance_assignments:
            if assignment.operation_start_date and assignment.maintenance_interval_days:
                next_maintenance = assignment.operation_start_date + timedelta(
                    days=assignment.maintenance_interval_days
                )
                if today <= next_maintenance <= today + timedelta(days=15):
                    days_until_maintenance = (next_maintenance - today).days
                    level = "high" if days_until_maintenance <= 3 else "medium"

                    alerts.append(
                        {
                            "type": "maintenance_due",
                            "level": level,
                            "message": (
                                f"Mantenimiento estimado en "
                                f"{days_until_maintenance} días"
                            ),
                            "equipment_name": assignment.resource_item.name,
                            "project_location": assignment.project.location,
                            "maintenance_date": next_maintenance,
                            "days_remaining": days_until_maintenance,
                        }
                    )

        return sorted(alerts, key=lambda x: x["days_remaining"])

    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Actividad reciente del partner (últimos 30 días)."""
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        activities = []

        # Proyectos creados recientemente
        recent_projects = Project.objects.filter(
            partner=self.partner, created_at__gte=thirty_days_ago, is_deleted=False
        ).order_by("-created_at")

        for project in recent_projects:
            activities.append(
                {
                    "type": "project_created",
                    "date": project.created_at.date(),
                    "description": (
                        f'Proyecto creado: {project.location or "Sin ubicación"}'
                    ),
                    "related_id": project.id,
                }
            )

        # Equipos asignados recientemente
        recent_assignments = (
            ProjectResourceItem.objects.filter(
                project__partner=self.partner,
                created_at__gte=thirty_days_ago,
                is_deleted=False,
            )
            .select_related("project", "resource_item")
            .order_by("-created_at")
        )

        for assignment in recent_assignments:
            activities.append(
                {
                    "type": "equipment_assigned",
                    "date": assignment.created_at.date(),
                    "description": (
                        f"Equipo {assignment.resource_item.name} asignado "
                        f"al proyecto {assignment.project.id}"
                    ),
                    "related_id": assignment.id,
                }
            )

        # Planillas creadas recientemente
        recent_sheets = (
            SheetProject.objects.filter(
                project__partner=self.partner,
                created_at__gte=thirty_days_ago,
                is_deleted=False,
            )
            .select_related("project")
            .order_by("-created_at")
        )

        for sheet in recent_sheets:
            activities.append(
                {
                    "type": "sheet_created",
                    "date": sheet.created_at.date(),
                    "description": (
                        f"Planilla {sheet.series_code} creada "
                        f"para proyecto {sheet.project.id}"
                    ),
                    "related_id": sheet.id,
                }
            )

        return sorted(activities, key=lambda x: x["date"], reverse=True)[:20]

    def _calculate_total_project_days(self) -> int:
        """Calcula el total de días de todos los proyectos."""
        projects = Project.objects.filter(
            partner=self.partner,
            is_deleted=False,
            start_date__isnull=False,
            end_date__isnull=False,
        )

        total_days = 0
        for project in projects:
            total_days += (project.end_date - project.start_date).days

        return total_days

    def _calculate_project_total_value(self, project: Project) -> Decimal:
        """Calcula el valor total de un proyecto específico."""
        assignments = ProjectResourceItem.objects.filter(
            project=project, is_deleted=False
        )

        total = Decimal("0.00")
        for assignment in assignments:
            total += assignment.rent_cost or Decimal("0.00")
            total += assignment.maintenance_cost or Decimal("0.00")

        return total

    def _calculate_assignment_total_value(
        self, assignment: ProjectResourceItem
    ) -> Decimal:
        """Calcula el valor total de una asignación de equipo."""
        rent = assignment.rent_cost or Decimal("0.00")
        maintenance = assignment.maintenance_cost or Decimal("0.00")

        # Si hay fechas, calcular por días
        if assignment.operation_start_date and assignment.operation_end_date:
            days = (
                assignment.operation_end_date - assignment.operation_start_date
            ).days
            return (rent + maintenance) * Decimal(str(days))

        return rent + maintenance

    def _calculate_average_project_value(self) -> Decimal:
        """Calcula el valor promedio de los proyectos."""
        projects = Project.objects.filter(partner=self.partner, is_deleted=False)

        if not projects.exists():
            return Decimal("0.00")

        total_value = Decimal("0.00")
        for project in projects:
            total_value += self._calculate_project_total_value(project)

        return total_value / Decimal(str(projects.count()))

    def _calculate_average_project_duration(self) -> float:
        """Calcula la duración promedio de los proyectos en días."""
        projects = Project.objects.filter(
            partner=self.partner,
            is_deleted=False,
            start_date__isnull=False,
            end_date__isnull=False,
        )

        if not projects.exists():
            return 0.0

        total_days = 0
        for project in projects:
            total_days += (project.end_date - project.start_date).days

        return total_days / projects.count()

    def _calculate_equipment_utilization_rate(self) -> float:
        """Calcula la tasa de utilización de equipos (%)."""
        today = timezone.now().date()

        total_assignments = ProjectResourceItem.objects.filter(
            project__partner=self.partner, project__is_deleted=False, is_deleted=False
        ).count()

        active_assignments = ProjectResourceItem.objects.filter(
            project__partner=self.partner,
            project__is_deleted=False,
            is_deleted=False,
            operation_start_date__lte=today,
            operation_end_date__gte=today,
            is_retired=False,
        ).count()

        if total_assignments == 0:
            return 0.0

        return (active_assignments / total_assignments) * 100


# Función de utilidad para uso directo
def get_partner_complete_info(partner_id: int) -> Dict[str, Any]:
    """
    Función utilitaria para obtener información completa de un partner.

    Args:
        partner_id (int): ID del partner

    Returns:
        Dict con toda la información del partner

    Raises:
        ValueError: Si el partner no existe
    """
    partner_info = PartnerCompleteInfo(partner_id)
    return partner_info.get_complete_information()


# Función para obtener múltiples partners
def get_multiple_partners_summary(partner_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Obtiene un resumen de múltiples partners.

    Args:
        partner_ids (List[int]): Lista de IDs de partners

    Returns:
        Lista con información resumida de cada partner
    """
    partners_summary = []

    for partner_id in partner_ids:
        try:
            partner_info = PartnerCompleteInfo(partner_id)
            basic_info = partner_info._get_partner_basic_info()
            projects_summary = partner_info._get_projects_summary()
            financial_summary = partner_info._get_financial_summary()

            partners_summary.append(
                {
                    "partner_id": partner_id,
                    "name": basic_info["name"],
                    "business_tax_id": basic_info["business_tax_id"],
                    "total_projects": projects_summary["total_projects"],
                    "active_projects": projects_summary["active_projects"],
                    "total_business_value": (financial_summary["total_business_value"]),
                    "is_active": basic_info["is_active"],
                }
            )
        except ValueError:
            # Partner no encontrado, continuar con el siguiente
            continue

    return partners_summary
