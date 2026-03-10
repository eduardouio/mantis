"""
EquipmentManager - Clase centralizada para la gestión integral de equipos.

Centraliza todas las operaciones de movimiento de equipos físicos:
asignación, retiro, reasignación, eliminación y control de disponibilidad.

Reglas de negocio:
- Un equipo físico (tipo != SERVIC) solo puede estar en UN proyecto a la vez.
- Un servicio (tipo == SERVIC) puede estar en múltiples proyectos.
- Al retirar un equipo se retiran automáticamente sus servicios asociados
  (vinculados por ``physical_equipment_code``).
- Al retirar un equipo se recalcula la planilla activa usando
  ``retirement_date`` como fecha fin.
- La reasignación de un equipo previamente retirado crea un NUEVO
  ``ProjectResourceItem``; el anterior queda como histórico.
- Los estados ``stst_status_disponibility`` del ``ResourceItem`` se
  mantienen sincronizados: DISPONIBLE / RENTADO.
"""

from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from equipment.models.ResourceItem import ResourceItem
from projects.models.Project import Project, ProjectResourceItem
from projects.models.CustodyChain import ChainCustodyDetail
from projects.models.SheetProject import SheetProject, SheetProjectDetail


class EquipmentManagerError(Exception):
    """Excepción base para errores de gestión de equipos."""
    pass


class EquipmentManager:
    """Gestor centralizado de operaciones sobre equipos y servicios."""

    # ------------------------------------------------------------------
    # Asignación
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def assign_to_project(
        cls,
        resource_item,
        project,
        cost,
        physical_equipment_code=0,
        frequency_type="DAY",
        interval_days=1,
        weekdays=None,
        monthdays=None,
        operation_start_date=None,
        commitment_date=None,
    ):
        """
        Asigna un equipo físico a un proyecto.

        Valida que el equipo esté DISPONIBLE antes de asignarlo.
        Actualiza los campos ``stst_*`` del ``ResourceItem`` y crea un
        ``ProjectResourceItem`` de tipo EQUIPO.

        Args:
            resource_item: Instancia de ``ResourceItem`` (tipo != SERVIC).
            project: Instancia de ``Project``.
            cost: Costo de alquiler (Decimal).
            physical_equipment_code: ID libre del equipo físico asociado.
            frequency_type: DAY | WEEK | MONTH.
            interval_days: Intervalo en días (para DAY).
            weekdays: Lista de días de la semana [0..6] (para WEEK).
            monthdays: Lista de días del mes [1..31] (para MONTH).
            operation_start_date: Fecha de inicio de operaciones.
            commitment_date: Fecha de compromiso de la renta.

        Returns:
            ProjectResourceItem creado.

        Raises:
            EquipmentManagerError: Si el equipo no está disponible o no es
            un equipo físico válido.
        """
        cls._validate_is_physical_equipment(resource_item)
        cls._validate_available(resource_item)

        detailed_description = cls._build_equipment_description(resource_item)

        if frequency_type == "DAY" and interval_days is None:
            interval_days = 1
        elif frequency_type != "DAY":
            interval_days = interval_days or 0

        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource_item,
            type_resource="EQUIPO",
            detailed_description=detailed_description,
            physical_equipment_code=physical_equipment_code or 0,
            cost=cost,
            frequency_type=frequency_type,
            interval_days=interval_days,
            weekdays=weekdays,
            monthdays=monthdays,
            operation_start_date=operation_start_date,
        )

        # Marcar equipo como RENTADO
        resource_item.stst_status_disponibility = "RENTADO"
        resource_item.stst_current_project_id = project.id
        resource_item.stst_current_location = project.location
        resource_item.stst_commitment_date = commitment_date
        resource_item.save(
            update_fields=[
                "stst_status_disponibility",
                "stst_current_project_id",
                "stst_current_location",
                "stst_commitment_date",
            ]
        )

        return project_resource

    @classmethod
    @transaction.atomic
    def assign_service_to_project(
        cls,
        resource_item,
        project,
        cost,
        physical_equipment_code=0,
        frequency_type="DAY",
        interval_days=1,
        weekdays=None,
        monthdays=None,
        operation_start_date=None,
    ):
        """
        Asigna un servicio a un proyecto.

        Los servicios **no** tienen restricción de disponibilidad y pueden
        estar en múltiples proyectos simultáneamente.

        Args:
            resource_item: Instancia de ``ResourceItem`` (tipo SERVIC o
                el recurso de servicio genérico).
            project: Instancia de ``Project``.
            cost: Costo del servicio (Decimal).
            physical_equipment_code: ID del equipo físico al que se vincula.
            frequency_type: DAY | WEEK | MONTH.
            interval_days: Intervalo en días (para DAY).
            weekdays: Lista de días de la semana [0..6] (para WEEK).
            monthdays: Lista de días del mes [1..31] (para MONTH).
            operation_start_date: Fecha de inicio de operaciones.

        Returns:
            ProjectResourceItem creado.
        """
        detailed_description = cls._build_service_description(
            resource_item, physical_equipment_code
        )

        if frequency_type == "DAY" and interval_days is None:
            interval_days = 1
        elif frequency_type != "DAY":
            interval_days = interval_days or 0

        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource_item,
            type_resource="SERVICIO",
            detailed_description=detailed_description,
            physical_equipment_code=physical_equipment_code or 0,
            cost=cost,
            frequency_type=frequency_type,
            interval_days=interval_days,
            weekdays=weekdays,
            monthdays=monthdays,
            operation_start_date=operation_start_date,
        )

        return project_resource

    # ------------------------------------------------------------------
    # Retiro
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def retire_from_project(cls, project_resource_id, retirement_reason=None):
        """
        Retira un recurso de un proyecto.

        - Si es tipo EQUIPO: limpia ``stst_*`` → DISPONIBLE, retira
          servicios asociados y recalcula la planilla activa.
        - Si es tipo SERVICIO: solo marca como retirado.

        Args:
            project_resource_id: ID del ``ProjectResourceItem``.
            retirement_reason: Motivo del retiro (opcional).

        Returns:
            dict con ``project_resource``, ``related_services_released``
            y ``message``.

        Raises:
            EquipmentManagerError: Si el recurso no existe o ya está
            retirado.
        """
        project_resource = cls._get_project_resource(project_resource_id)

        if project_resource.is_retired:
            raise EquipmentManagerError("El recurso ya se encuentra retirado.")

        today = timezone.now().date()

        project_resource.is_retired = True
        project_resource.retirement_date = today
        if retirement_reason:
            project_resource.retirement_reason = retirement_reason
        project_resource.save(
            update_fields=["is_retired", "retirement_date", "retirement_reason"]
        )

        released_services = []

        if project_resource.type_resource == "EQUIPO":
            # Liberar el equipo físico
            cls._release_equipment_status(project_resource.resource_item)

            # Retirar servicios asociados
            released_services = cls._retire_related_services(
                project_resource, today, retirement_reason
            )

        # Recalcular planillas activas
        cls._recalculate_active_sheets(project_resource)

        return {
            "project_resource": project_resource,
            "related_services_released": [s.id for s in released_services],
            "message": (
                "Equipo liberado correctamente."
                if project_resource.type_resource == "EQUIPO"
                else "Servicio liberado correctamente."
            ),
        }

    # ------------------------------------------------------------------
    # Reasignación
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def reassign_to_project(
        cls,
        resource_item,
        project,
        cost,
        physical_equipment_code=0,
        frequency_type="DAY",
        interval_days=1,
        weekdays=None,
        monthdays=None,
        operation_start_date=None,
        commitment_date=None,
    ):
        """
        Reasigna un equipo previamente retirado al mismo u otro proyecto.

        Internamente valida disponibilidad y crea un NUEVO
        ``ProjectResourceItem``. El registro anterior debe existir como
        retirado para garantizar trazabilidad.

        Args:
            (mismos que ``assign_to_project``)

        Returns:
            ProjectResourceItem creado.

        Raises:
            EquipmentManagerError: Si el equipo no está disponible.
        """
        return cls.assign_to_project(
            resource_item=resource_item,
            project=project,
            cost=cost,
            physical_equipment_code=physical_equipment_code,
            frequency_type=frequency_type,
            interval_days=interval_days,
            weekdays=weekdays,
            monthdays=monthdays,
            operation_start_date=operation_start_date,
            commitment_date=commitment_date,
        )

    # ------------------------------------------------------------------
    # Eliminación
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def delete_from_project(cls, project_resource_id):
        """
        Elimina físicamente un recurso de un proyecto.

        Validaciones:
        - No debe estar referenciado en ``ChainCustodyDetail``.
        - No debe estar referenciado en ``SheetProjectDetail`` de
          planillas cerradas.

        Si es tipo EQUIPO, también elimina sus servicios asociados
        (con las mismas validaciones) y libera el estado del equipo.

        Args:
            project_resource_id: ID del ``ProjectResourceItem``.

        Returns:
            dict con ``deleted_id`` y ``related_deleted``.

        Raises:
            EquipmentManagerError: Si tiene referencias en cadenas de
            custodia o planillas cerradas.
        """
        project_resource = cls._get_project_resource(project_resource_id)

        cls._validate_can_delete(project_resource)

        related_deleted = []

        if project_resource.type_resource == "EQUIPO":
            # Eliminar servicios asociados primero
            related_services = cls._find_related_services(project_resource)
            for service in related_services:
                cls._validate_can_delete(service)

            for service in related_services:
                cls._clean_sheet_details(service)
                related_deleted.append(service.id)
                service.delete()

            # Liberar estado del equipo
            cls._release_equipment_status(project_resource.resource_item)

        # Limpiar detalles de planilla abierta referenciados
        cls._clean_sheet_details(project_resource)

        project_resource.delete()

        return {
            "deleted_id": project_resource_id,
            "related_deleted": related_deleted,
        }

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    @classmethod
    def check_availability(cls, resource_item_id):
        """
        Verifica la disponibilidad real de un equipo.

        Consulta tanto ``stst_status_disponibility`` como la existencia de
        ``ProjectResourceItem`` activos no retirados.

        Args:
            resource_item_id: ID del ``ResourceItem``.

        Returns:
            dict con ``available`` (bool), ``status``, ``active_project``
            (id o None).
        """
        try:
            resource_item = ResourceItem.objects.get(id=resource_item_id)
        except ResourceItem.DoesNotExist:
            raise EquipmentManagerError(
                f"Equipo con ID {resource_item_id} no encontrado."
            )

        active_assignment = ProjectResourceItem.objects.filter(
            resource_item=resource_item,
            type_resource="EQUIPO",
            is_active=True,
            is_retired=False,
            project__is_closed=False,
            project__is_deleted=False,
        ).select_related("project").first()

        status = resource_item.stst_status_disponibility or "DISPONIBLE"
        is_available = status == "DISPONIBLE" and active_assignment is None

        return {
            "available": is_available,
            "status": status,
            "active_project": (
                active_assignment.project.id if active_assignment else None
            ),
            "active_project_resource_id": (
                active_assignment.id if active_assignment else None
            ),
        }

    @classmethod
    def get_equipment_history(cls, resource_item_id, project_id=None):
        """
        Obtiene el historial completo de asignaciones de un equipo.

        Args:
            resource_item_id: ID del ``ResourceItem``.
            project_id: Si se proporciona, filtra por proyecto.

        Returns:
            list[dict] con los datos de cada asignación.
        """
        filters = {
            "resource_item_id": resource_item_id,
            "type_resource": "EQUIPO",
        }
        if project_id:
            filters["project_id"] = project_id

        assignments = (
            ProjectResourceItem.objects.filter(**filters)
            .select_related("project", "resource_item")
            .order_by("-operation_start_date", "-id")
        )

        history = []
        for pr in assignments:
            history.append(
                {
                    "id": pr.id,
                    "project_id": pr.project.id,
                    "project_name": str(pr.project),
                    "operation_start_date": (
                        pr.operation_start_date.isoformat()
                        if pr.operation_start_date
                        else None
                    ),
                    "operation_end_date": (
                        pr.operation_end_date.isoformat()
                        if pr.operation_end_date
                        else None
                    ),
                    "is_retired": pr.is_retired,
                    "retirement_date": (
                        pr.retirement_date.isoformat()
                        if pr.retirement_date
                        else None
                    ),
                    "retirement_reason": pr.retirement_reason,
                    "cost": float(pr.cost),
                    "is_active": pr.is_active,
                }
            )

        return history

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    @classmethod
    def _validate_is_physical_equipment(cls, resource_item):
        """Valida que el recurso sea un equipo físico (NO servicio)."""
        if resource_item.type_equipment == "SERVIC":
            raise EquipmentManagerError(
                f"El recurso {resource_item.code} es un servicio, "
                "no un equipo físico. Use assign_service_to_project()."
            )

    @classmethod
    def _validate_available(cls, resource_item):
        """Valida que el equipo esté DISPONIBLE para asignar."""
        status = resource_item.stst_status_disponibility or "DISPONIBLE"
        if status != "DISPONIBLE":
            raise EquipmentManagerError(
                f"El equipo {resource_item.code} no está disponible. "
                f"Estado actual: {status}."
            )

        # Verificación adicional: no debe tener asignaciones activas
        active = ProjectResourceItem.objects.filter(
            resource_item=resource_item,
            type_resource="EQUIPO",
            is_active=True,
            is_retired=False,
            project__is_closed=False,
        ).exists()

        if active:
            raise EquipmentManagerError(
                f"El equipo {resource_item.code} tiene una asignación activa "
                "en un proyecto. Debe retirarlo antes de reasignarlo."
            )

    @classmethod
    def _get_project_resource(cls, project_resource_id):
        """Obtiene un ProjectResourceItem por ID o lanza error."""
        try:
            return ProjectResourceItem.objects.select_related(
                "project", "resource_item"
            ).get(id=project_resource_id)
        except ProjectResourceItem.DoesNotExist:
            raise EquipmentManagerError(
                f"Recurso de proyecto con ID {project_resource_id} no encontrado."
            )

    @classmethod
    def _release_equipment_status(cls, resource_item):
        """Limpia los campos stst_* del equipo y lo marca DISPONIBLE."""
        resource_item.stst_status_disponibility = "DISPONIBLE"
        resource_item.stst_current_project_id = None
        resource_item.stst_current_location = None
        resource_item.stst_commitment_date = None
        resource_item.stst_release_date = None
        resource_item.save(
            update_fields=[
                "stst_status_disponibility",
                "stst_current_project_id",
                "stst_current_location",
                "stst_commitment_date",
                "stst_release_date",
            ]
        )

    @classmethod
    def _find_related_services(cls, project_resource):
        """
        Encuentra servicios asociados a un equipo en el mismo proyecto.

        La vinculación se hace por ``physical_equipment_code`` que almacena
        el ``resource_item.id`` del equipo físico.
        """
        equipment_id = project_resource.resource_item.id
        related_codes = {equipment_id}

        physical_code = project_resource.physical_equipment_code
        if physical_code and physical_code > 0:
            related_codes.add(physical_code)

        return list(
            ProjectResourceItem.objects.filter(
                project=project_resource.project,
                type_resource="SERVICIO",
                physical_equipment_code__in=list(related_codes),
                is_retired=False,
                is_active=True,
            )
        )

    @classmethod
    def _retire_related_services(cls, project_resource, today, reason=None):
        """Retira servicios asociados a un equipo y recalcula sus planillas."""
        related = cls._find_related_services(project_resource)
        for service in related:
            service.is_retired = True
            service.retirement_date = today
            if reason:
                service.retirement_reason = reason
            service.save(
                update_fields=["is_retired", "retirement_date", "retirement_reason"]
            )
            cls._recalculate_active_sheets(service)
        return related

    @classmethod
    def _recalculate_active_sheets(cls, project_resource):
        """
        Recalcula los SheetProjectDetail de planillas abiertas que
        referencien a este ProjectResourceItem.

        Usa la lógica de ``WorkSheetBuilder.calculate_rental_days`` para
        recalcular los días considerando la fecha de retiro.
        """
        # Importar aquí para evitar importación circular
        from common.WorkSheetBuilder import WorkSheetBuilder

        details = SheetProjectDetail.objects.filter(
            project_resource_item=project_resource,
            is_closed=False,
            sheet_project__is_closed=False,
            is_active=True,
        ).select_related("sheet_project")

        for detail in details:
            builder = WorkSheetBuilder(detail.sheet_project)

            if project_resource.type_resource == "EQUIPO":
                days_dict = builder.calculate_rental_days(project_resource)
                monthdays_list = sorted(
                    [day for day, count in days_dict.items() if count > 0]
                )
                quantity = sum(days_dict.values())
            else:
                monthdays_list = builder.calculate_service_days(project_resource)
                quantity = len(monthdays_list)

            detail.monthdays_apply_cost = monthdays_list
            detail.quantity = Decimal(str(quantity))
            detail.total_line = detail.quantity * detail.unit_price

            if quantity == 0:
                # El recurso no tiene días en este período (se retiró antes del inicio).
                # Desactivar el detalle para que no aparezca en la planilla.
                detail.is_active = False
                detail.is_deleted = True
                detail.save(
                    update_fields=[
                        "monthdays_apply_cost",
                        "quantity",
                        "total_line",
                        "is_active",
                        "is_deleted",
                    ]
                )
            else:
                detail.save(
                    update_fields=[
                        "monthdays_apply_cost",
                        "quantity",
                        "total_line",
                    ]
                )

    @classmethod
    def _validate_can_delete(cls, project_resource):
        """
        Valida que un ProjectResourceItem puede ser eliminado.

        No se puede eliminar si está referenciado en:
        - ChainCustodyDetail
        - SheetProjectDetail de planillas cerradas
        """
        custody_refs = ChainCustodyDetail.get_by_resource_id(project_resource.id)
        if custody_refs:
            raise EquipmentManagerError(
                f"No se puede eliminar el recurso '{project_resource.detailed_description}' "
                "porque ha sido utilizado en una cadena de custodia."
            )

        closed_sheet_refs = SheetProjectDetail.objects.filter(
            project_resource_item=project_resource,
            sheet_project__is_closed=True,
            is_active=True,
        ).exists()
        if closed_sheet_refs:
            raise EquipmentManagerError(
                f"No se puede eliminar el recurso '{project_resource.detailed_description}' "
                "porque está referenciado en una planilla cerrada."
            )

    @classmethod
    def _clean_sheet_details(cls, project_resource):
        """Elimina SheetProjectDetail de planillas abiertas para este recurso."""
        SheetProjectDetail.objects.filter(
            project_resource_item=project_resource,
            sheet_project__is_closed=False,
        ).delete()

    @classmethod
    def _build_equipment_description(cls, resource_item):
        """Construye la descripción formateada para un equipo."""
        type_label = resource_item.get_type_equipment_display()
        return f"ALQUILER / {resource_item.code} / {type_label}"

    @classmethod
    def _build_service_description(cls, resource_item, physical_equipment_code):
        """Construye la descripción formateada para un servicio."""
        if physical_equipment_code and physical_equipment_code > 0:
            try:
                physical = ResourceItem.objects.get(id=physical_equipment_code)
                return f"SERVICIO / {physical.code} / {resource_item.name.upper()}"
            except ResourceItem.DoesNotExist:
                pass
        return f"SERVICIO / {resource_item.code} / {resource_item.name.upper()}"
