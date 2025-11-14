from django.http import JsonResponse
from django.views import View
from django.apps import apps
from decimal import Decimal
from datetime import date, datetime


class CustodyChainDetaikAPI(View):
    """Detalle completo de una cadena de custodia con dependencias y metadatos."""

    def get(self, request, id):
        chain_id = id

        try:

            CustodyChain = apps.get_model("projects", "CustodyChain")
        except LookupError:
            return JsonResponse(
                {"success": False, "error": "Modelo CustodyChain no encontrado."},
                status=500,
            )

        try:
            instance = (
                CustodyChain.objects.select_related(
                    "technical", "vehicle", "sheet_project"
                )
                .prefetch_related(
                    "chaincustodydetail_set__project_resource",
                    "chaincustodydetail_set__project_resource__project",
                    "chaincustodydetail_set__project_resource__resource_item",
                )
                .get(pk=chain_id)
            )
        except CustodyChain.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Cadena de custodia no encontrada."},
                status=404,
            )

        def serialize_date(value):
            if isinstance(value, (date, datetime)):
                return value.isoformat()
            return value

        def coerce_value(value):
            if isinstance(value, Decimal):
                return float(value)
            return serialize_date(value)

        def serialize_meta(obj):
            return {
                "notes": getattr(obj, "notes", None),
                "created_at": serialize_date(getattr(obj, "created_at", None)),
                "updated_at": serialize_date(getattr(obj, "updated_at", None)),
                "is_active": getattr(obj, "is_active", None),
                "is_deleted": getattr(obj, "is_deleted", None),
                "id_user_created": getattr(obj, "id_user_created", None),
                "id_user_updated": getattr(obj, "id_user_updated", None),
            }

        def has_attr(obj, name):
            return hasattr(obj, name)

        def serialize_instance(obj, depth=2, visited=None, is_root=False):
            if visited is None:
                visited = set()

            model_label = f"{obj._meta.app_label}.{obj._meta.model_name}"
            key = (model_label, obj.pk)
            if key in visited:
                return {"_ref": {"model": model_label, "id": obj.pk}}
            visited.add(key)

            data = {"id": obj.pk}

            for field in obj._meta.concrete_fields:
                fname = field.name
                try:
                    value = getattr(obj, fname)
                except Exception:
                    continue

                if field.is_relation and field.many_to_one and value is not None:
                    data[f"{fname}_id"] = getattr(obj, f"{fname}_id", None)
                    if depth > 0:
                        try:
                            data[fname] = serialize_instance(
                                value, depth=depth - 1, visited=visited
                            )
                        except Exception:
                            data[fname] = str(value)
                else:
                    data[fname] = coerce_value(value)

            for m2m in obj._meta.many_to_many:
                try:
                    manager = getattr(obj, m2m.name)
                except Exception:
                    continue
                items_qs = manager.all()
                if has_attr(items_qs.model, "is_active"):
                    items_qs = items_qs.filter(is_active=True)

                if depth > 0:
                    data[m2m.name] = [
                        serialize_instance(child, depth=depth - 1, visited=visited)
                        for child in items_qs
                    ]
                else:
                    data[m2m.name] = [child.pk for child in items_qs]

            for rel in obj._meta.get_fields():
                if not (rel.auto_created and (rel.one_to_many or rel.many_to_many)):
                    continue
                accessor = rel.get_accessor_name()
                try:
                    manager = getattr(obj, accessor)
                except Exception:
                    continue

                try:
                    child_qs = manager.all()
                except Exception:
                    continue

                if hasattr(child_qs.model, "is_active"):
                    child_qs = child_qs.filter(is_active=True)

                if depth > 0:
                    data[accessor] = [
                        serialize_instance(child, depth=depth - 1, visited=visited)
                        for child in child_qs
                    ]
                else:
                    data[accessor] = [child.pk for child in child_qs]

            meta = serialize_meta(obj)
            data["meta"] = meta

            if is_root:
                data.update(
                    {
                        "notes": meta["notes"],
                        "created_at": meta["created_at"],
                        "updated_at": meta["updated_at"],
                        "is_active": meta["is_active"],
                        "is_deleted": meta["is_deleted"],
                        "id_user_created": meta["id_user_created"],
                        "id_user_updated": meta["id_user_updated"],
                    }
                )

            return data

        serialized = serialize_instance(instance, depth=3, is_root=True)
        return JsonResponse({"success": True, "data": serialized})
