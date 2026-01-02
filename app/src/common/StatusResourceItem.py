"""
StatusResourceItem - Clase de verificación y limpieza del estado de equipos

Esta clase se encarga de:
1. Verificar si un equipo está completo según su checklist
2. Determinar si está disponible para rentar o ya está rentado
3. Limpiar datos inconsistentes (equipos marcados como rentados sin
   proyecto vigente)
4. Retornar información completa del estado del equipo
5. Actualizar automáticamente la ficha del equipo

Que la fuerza te acompañe!
"""

from datetime import date
from django.db import transaction
from django.utils import timezone
from equipment.models.ResourceItem import ResourceItem
from projects.models.Project import Project, ProjectResourceItem


class StatusResourceItem:
    """Verificador y limpiador del estado de equipos."""

    def __init__(self, resource_item: ResourceItem):
        """
        Inicializa el verificador de estado.

        Args:
            resource_item: Instancia del equipo a verificar
        """
        self.resource_item = resource_item
        self.status_data = {}
        self._analyze_equipment()

    def _analyze_equipment(self) -> None:
        """Analiza completamente el estado del equipo."""

        self.status_data["equipment_info"] = {
            "id": self.resource_item.id,
            "code": self.resource_item.code,
            "name": self.resource_item.name,
            "type_equipment": self.resource_item.type_equipment,
            "is_service": getattr(self.resource_item, "is_service", False),
            "is_active": self.resource_item.is_active,
        }

        if getattr(self.resource_item, "is_service", False):
            self._analyze_service()
        else:
            self._analyze_physical_equipment()

    def _analyze_service(self) -> None:
        """Analiza el estado de un servicio."""
        self.status_data.update(
            {
                "is_complete": True,
                "completion_percentage": 100.0,
                "missing_items": [],
                "availability_status": "DISPONIBLE",
                "rental_info": None,
                "project_info": None,
                "inconsistencies_found": [],
                "needs_update": False,
                "recommendations": ["Servicio listo para ser contratado"],
            }
        )

    def _analyze_physical_equipment(self) -> None:
        """Analiza el estado de un equipo físico."""

        self._check_equipment_completeness()

        self._check_availability_and_projects()

        self._check_and_clean_inconsistencies()

        self._generate_recommendations()

    def _check_equipment_completeness(self) -> None:
        """Verifica si el equipo está completo según su checklist."""
        boolean_fields = self.resource_item.boolean_fields

        if not boolean_fields:

            checklist_msg = "No hay checklist definido para este tipo " "de equipo"
            self.status_data.update(
                {
                    "is_complete": True,
                    "completion_percentage": 100.0,
                    "missing_items": [],
                    "checklist_info": checklist_msg,
                }
            )
            return

        total_items = len(boolean_fields)
        complete_items = 0
        missing_items = []

        for field_name in boolean_fields:
            field_value = self.resource_item.get_field_value(field_name)
            field_label = self.resource_item.get_field_label(field_name)

            if field_value:
                complete_items += 1
            else:
                missing_items.append({"field": field_name, "label": field_label})

        if total_items > 0:
            completion_percentage = complete_items / total_items * 100
        else:
            completion_percentage = 100

        self.status_data.update(
            {
                "is_complete": len(missing_items) == 0,
                "completion_percentage": round(completion_percentage, 2),
                "missing_items": missing_items,
                "checklist_info": {
                    "total_items": total_items,
                    "complete_items": complete_items,
                    "missing_count": len(missing_items),
                },
            }
        )

    def _check_availability_and_projects(self) -> None:
        """Verifica disponibilidad y estado de proyectos."""
        current_status = getattr(
            self.resource_item, "stst_status_disponibility", "DISPONIBLE"
        )
        current_project_id = getattr(
            self.resource_item, "stst_current_project_id", None
        )
        commitment_date = getattr(self.resource_item, "stst_commitment_date", None)
        release_date = getattr(self.resource_item, "stst_release_date", None)
        current_location = getattr(self.resource_item, "stst_current_location", None)

        self.status_data["availability_status"] = current_status

        project_info = None
        rental_info = None

        if current_project_id:
            project_info = self._get_project_info(current_project_id)
            if project_info:
                rental_info = self._get_rental_info(
                    project_info["project"], commitment_date, release_date
                )

        self.status_data.update(
            {
                "project_info": project_info,
                "rental_info": rental_info,
                "current_location": current_location,
                "commitment_date": commitment_date,
                "release_date": release_date,
            }
        )

    def _get_project_info(self, project_id: int):
        """Obtiene información del proyecto asociado."""
        try:
            project = Project.objects.get(
                id=project_id, is_active=True, is_deleted=False
            )

            project_resource = ProjectResourceItem.objects.filter(
                project=project,
                resource_item=self.resource_item,
                is_active=True,
                is_deleted=False,
                is_retired=False,
            ).first()

            project_info = {
                "project": project,
                "project_id": project.id,
                "partner_name": (
                    project.partner.name if hasattr(project, "partner") else "N/A"
                ),
                "contact_name": project.contact_name,
                "contact_phone": project.contact_phone,
                "location": project.location,
                "project_start_date": project.start_date,
                "project_end_date": project.end_date,
                "is_closed": project.is_closed,
                "project_resource_relation": project_resource,
            }

            if project_resource:
                # Solo incluir atributos que existen en el modelo
                if hasattr(project_resource, 'rent_cost'):
                    project_info['rent_cost'] = project_resource.rent_cost
                if hasattr(project_resource, 'maintenance_cost'):
                    project_info['maintenance_cost'] = project_resource.maintenance_cost
                if hasattr(project_resource, 'maintenance_interval_days'):
                    project_info['maintenance_interval_days'] = project_resource.maintenance_interval_days
                if hasattr(project_resource, 'operation_start_date'):
                    project_info['operation_start_date'] = project_resource.operation_start_date
                if hasattr(project_resource, 'operation_end_date'):
                    project_info['operation_end_date'] = project_resource.operation_end_date

            return project_info

        except Project.DoesNotExist:
            return None

    def _get_rental_info(
        self, project: Project, commitment_date: date, release_date: date
    ):
        """Genera información de renta del equipo."""
        today = date.today()

        rental_info = {
            "is_currently_rented": True,
            "rental_start_date": commitment_date,
            "rental_end_date": release_date,
            "project_partner": (
                project.partner.name if hasattr(project, "partner") else "N/A"
            ),
            "project_location": project.location,
            "project_contact": f"{project.contact_name} - {project.contact_phone}",
        }

        if commitment_date and release_date:
            rental_days = (release_date - commitment_date).days
            rental_info["total_rental_days"] = rental_days

            if release_date >= today:
                remaining_days = (release_date - today).days
                rental_info["remaining_days"] = remaining_days
                rental_info["rental_status"] = "ACTIVO"
            else:
                rental_info["remaining_days"] = 0
                rental_info["rental_status"] = "VENCIDO"

        if project.is_closed:
            rental_info["rental_status"] = "PROYECTO_CERRADO"
            rental_info["needs_return"] = True

        return rental_info

    def _check_and_clean_inconsistencies(self) -> None:
        """Detecta y limpia inconsistencias en los datos."""
        inconsistencies = []
        needs_update = False

        current_status = self.status_data["availability_status"]
        project_info = self.status_data["project_info"]

        if current_status == "RENTADO" and not project_info:
            inconsistencies.append(
                {
                    "type": "NO_VALID_PROJECT",
                    "description": "Equipo marcado como RENTADO pero no tiene proyecto vigente asociado",
                    "action": "Cambiar estado a DISPONIBLE y limpiar datos de proyecto",
                }
            )
            needs_update = True

        if (
            current_status == "RENTADO"
            and project_info
            and project_info.get("is_closed", False)
        ):
            inconsistencies.append(
                {
                    "type": "CLOSED_PROJECT",
                    "description": "Equipo rentado en proyecto cerrado",
                    "action": "Cambiar estado a DISPONIBLE y limpiar datos de proyecto",
                }
            )
            needs_update = True

        release_date = self.status_data.get("release_date")
        if current_status == "RENTADO" and release_date and release_date < date.today():
            inconsistencies.append(
                {
                    "type": "EXPIRED_RENTAL",
                    "description": f"Fecha de liberación vencida: {release_date}",
                    "action": "Verificar estado del proyecto y actualizar fechas o liberar equipo",
                }
            )

        if (
            current_status == "DISPONIBLE"
            and project_info
            and not project_info.get("is_closed", True)
        ):
            project_resource = project_info.get("project_resource_relation")
            if project_resource and not project_resource.is_retired:
                inconsistencies.append(
                    {
                        "type": "ACTIVE_PROJECT_AVAILABLE_EQUIPMENT",
                        "description": "Equipo marcado como DISPONIBLE pero está asociado a proyecto activo",
                        "action": "Cambiar estado a RENTADO o retirar del proyecto",
                    }
                )

        self.status_data.update(
            {"inconsistencies_found": inconsistencies, "needs_update": needs_update}
        )

    def _generate_recommendations(self) -> None:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []

        if not self.status_data["is_complete"]:
            missing_count = len(self.status_data["missing_items"])
            recommendations.append(
                f"Completar checklist: faltan {missing_count} elementos"
            )

        if self.status_data["availability_status"] == "DISPONIBLE":
            if self.status_data["is_complete"]:
                recommendations.append("Equipo listo para rentar")
            else:
                recommendations.append("Completar checklist antes de rentar")

        if self.status_data["inconsistencies_found"]:
            recommendations.append("Resolver inconsistencias encontradas")

        rental_info = self.status_data.get("rental_info")
        if rental_info:
            if rental_info.get("rental_status") == "VENCIDO":
                recommendations.append("Contactar cliente para renovación o devolución")
            elif rental_info.get("needs_return"):
                recommendations.append("Coordinar devolución del equipo")
            elif rental_info.get("remaining_days", 0) <= 7:
                recommendations.append("Próximo a vencer: contactar cliente")

        self.status_data["recommendations"] = recommendations

    @transaction.atomic
    def update_equipment_status(self):
        """Actualiza automáticamente la ficha del equipo según las inconsistencias encontradas."""
        if not self.status_data["needs_update"]:
            return {"updated": False, "message": "No se requieren actualizaciones"}

        updates_made = []

        for inconsistency in self.status_data["inconsistencies_found"]:
            if inconsistency["type"] in ["NO_VALID_PROJECT", "CLOSED_PROJECT"]:

                self.resource_item.stst_status_disponibility = "DISPONIBLE"
                self.resource_item.stst_current_project_id = None
                self.resource_item.stst_current_location = None
                self.resource_item.stst_commitment_date = None
                self.resource_item.stst_release_date = None

                updates_made.append(
                    f"Estado cambiado a DISPONIBLE - {inconsistency['description']}"
                )

        if updates_made:
            self.resource_item.save()

            self._analyze_equipment()

        return {
            "updated": True,
            "updates_made": updates_made,
            "message": f"Se realizaron {len(updates_made)} actualizaciones",
        }

    def get_status_report(self):
        """Retorna el reporte completo del estado del equipo."""
        return {
            "timestamp": timezone.now(),
            "equipment_info": self.status_data["equipment_info"],
            "completeness": {
                "is_complete": self.status_data["is_complete"],
                "completion_percentage": self.status_data["completion_percentage"],
                "missing_items": self.status_data["missing_items"],
                "checklist_info": self.status_data.get("checklist_info", {}),
            },
            "availability": {
                "status": self.status_data["availability_status"],
                "current_location": self.status_data.get("current_location"),
                "commitment_date": self.status_data.get("commitment_date"),
                "release_date": self.status_data.get("release_date"),
            },
            "project_info": self.status_data.get("project_info"),
            "rental_info": self.status_data.get("rental_info"),
            "inconsistencies": {
                "found": self.status_data["inconsistencies_found"],
                "needs_update": self.status_data["needs_update"],
            },
            "recommendations": self.status_data["recommendations"],
        }

    @classmethod
    def analyze_equipment(cls, equipment_id: int, auto_update: bool = False):
        """
        Método de clase para analizar un equipo por ID.

        Args:
            equipment_id: ID del equipo a analizar
            auto_update: Si True, actualiza automáticamente las inconsistencias

        Returns:
            Dict con el reporte completo del estado
        """
        try:
            resource_item = ResourceItem.objects.get(
                id=equipment_id, is_active=True, is_deleted=False
            )
            analyzer = cls(resource_item)

            report = analyzer.get_status_report()

            if auto_update:
                update_result = analyzer.update_equipment_status()
                report["auto_update_result"] = update_result

                if update_result["updated"]:
                    report = analyzer.get_status_report()
                    report["auto_update_result"] = update_result

            return report

        except ResourceItem.DoesNotExist:
            return {
                "error": True,
                "message": f"Equipo con ID {equipment_id} no encontrado",
            }

    @classmethod
    def bulk_analyze_and_clean(cls, equipment_ids: list = None):
        """
        Analiza y limpia múltiples equipos.

        Args:
            equipment_ids: Lista de IDs a analizar. Si None, analiza todos los equipos activos.

        Returns:
            Dict con resumen de resultados
        """
        if equipment_ids:
            equipments = ResourceItem.objects.filter(
                id__in=equipment_ids, is_active=True, is_deleted=False
            )
        else:
            equipments = ResourceItem.objects.filter(is_active=True, is_deleted=False)

        results = {
            "total_analyzed": 0,
            "equipments_with_issues": 0,
            "equipments_updated": 0,
            "total_inconsistencies": 0,
            "summary": [],
            "detailed_reports": [],
        }

        for equipment in equipments:
            analyzer = cls(equipment)
            report = analyzer.get_status_report()

            results["total_analyzed"] += 1

            if report["inconsistencies"]["found"]:
                results["equipments_with_issues"] += 1
                results["total_inconsistencies"] += len(
                    report["inconsistencies"]["found"]
                )

                update_result = analyzer.update_equipment_status()
                if update_result["updated"]:
                    results["equipments_updated"] += 1

                report["auto_update_result"] = update_result

            results["summary"].append(
                {
                    "equipment_id": equipment.id,
                    "equipment_code": equipment.code,
                    "equipment_name": equipment.name,
                    "has_issues": len(report["inconsistencies"]["found"]) > 0,
                    "is_complete": report["completeness"]["is_complete"],
                    "completion_percentage": report["completeness"][
                        "completion_percentage"
                    ],
                    "availability_status": report["availability"]["status"],
                }
            )

            results["detailed_reports"].append(report)

        return results


def check_equipment_status(equipment_id: int, auto_update: bool = False):
    """
    Función de utilidad para verificar el estado de un equipo.

    Args:
        equipment_id: ID del equipo a verificar
        auto_update: Si True, corrige automáticamente las inconsistencias

    Returns:
        Dict con el estado completo del equipo
    """
    return StatusResourceItem.analyze_equipment(equipment_id, auto_update)
