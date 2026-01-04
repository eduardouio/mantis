from django.views.generic import DetailView
from equipment.models import Vehicle, PassVehicle, CertificationVehicle
from common.VehicleIssuesCheck import VehicleIssuesCheck
from datetime import date


class VehicleStatusReport(DetailView):
    model = Vehicle
    template_name = 'reports/vehicle_report.html'
    context_object_name = 'vehicle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.object

        # Información General
        context['general_fields'] = [
            {'label': 'Placa', 'value': vehicle.no_plate},
            {'label': 'Tipo de Vehículo', 'value': vehicle.get_type_vehicle_display()},
            {'label': 'Marca', 'value': vehicle.brand},
            {'label': 'Modelo', 'value': vehicle.model},
            {'label': 'Año', 'value': vehicle.year},
            {'label': 'Color', 'value': vehicle.color},
            {'label': 'Propietario', 'value': vehicle.owner_transport},
            {'label': 'Estado', 'value': vehicle.get_status_vehicle_display()},
        ]

        # Datos Técnicos
        context['technical_fields'] = [
            {'label': 'Número de Chasis', 'value': vehicle.chassis_number},
            {'label': 'Número de Motor', 'value': vehicle.engine_number},
            {'label': 'Número de Serie', 'value': vehicle.serial_number},
        ]

        # Información de Seguros
        context['insurance_fields'] = [
            {'label': 'Compañía de Seguros', 'value': vehicle.insurance_company},
            {'label': 'Número de Póliza', 'value': vehicle.nro_poliza},
            {'label': 'Fecha Emisión Póliza', 'value': vehicle.insurance_issue_date.strftime('%d/%m/%Y') if vehicle.insurance_issue_date else None},
            {'label': 'Fecha Vencimiento Póliza', 'value': vehicle.insurance_expiration_date.strftime('%d/%m/%Y') if vehicle.insurance_expiration_date else None},
            {'label': 'Fecha Emisión Satelital', 'value': vehicle.date_satellite.strftime('%d/%m/%Y') if vehicle.date_satellite else None},
            {'label': 'Fecha Vencimiento Satelital', 'value': vehicle.due_date_satellite.strftime('%d/%m/%Y') if vehicle.due_date_satellite else None},
        ]

        # Documentos y Certificados con evaluación de estado
        documents = [
            {'label': 'Matrícula', 'date': vehicle.date_matricula, 'due_date': vehicle.due_date_matricula, 'field': 'due_date_matricula'},
            {'label': 'Certificado de Operación', 'date': vehicle.date_cert_oper, 'due_date': vehicle.due_date_cert_oper, 'field': 'due_date_cert_oper'},
            {'label': 'MTOP', 'date': vehicle.date_mtop, 'due_date': vehicle.due_date_mtop, 'field': 'due_date_mtop'},
            {'label': 'Revisión Técnica', 'date': vehicle.date_technical_review, 'due_date': vehicle.due_date_technical_review, 'field': 'due_date_technical_review'},
        ]

        # Evaluar estado de cada documento
        for doc in documents:
            if doc['due_date']:
                status, days_left = VehicleIssuesCheck._evaluate(doc['due_date'])
                doc['status'] = status
                doc['days_left'] = days_left
                if status == 'expired':
                    doc['status_class'] = 'status-expired'
                    doc['status_text'] = f'VENCIDO ({abs(days_left)} días)'
                elif status == 'due_10':
                    doc['status_class'] = 'status-due-10'
                    doc['status_text'] = f'POR VENCER ({days_left} días)'
                elif status == 'due_30':
                    doc['status_class'] = 'status-due-30'
                    doc['status_text'] = f'PRÓXIMO A VENCER ({days_left} días)'
                else:
                    doc['status_class'] = 'status-valid'
                    doc['status_text'] = f'VIGENTE ({days_left} días)'
            else:
                doc['status_class'] = 'status-na'
                doc['status_text'] = 'NO REGISTRADO'

        context['documents'] = documents

        # Pases de Bloques
        passes = PassVehicle.get_by_vehicle(vehicle.id)
        passes_data = []
        for p in passes:
            pass_data = {
                'bloque': p.bloque,
                'fecha_caducidad': p.fecha_caducidad.strftime('%d/%m/%Y') if p.fecha_caducidad else 'N/A',
            }
            if p.fecha_caducidad:
                status, days_left = VehicleIssuesCheck._evaluate(p.fecha_caducidad)
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

        # Certificaciones
        certifications = CertificationVehicle.objects.filter(vehicle=vehicle, is_active=True)
        certifications_data = []
        for cert in certifications:
            cert_data = {
                'name': cert.get_name_display(),
                'date_start': cert.date_start.strftime('%d/%m/%Y') if cert.date_start else 'N/A',
                'date_end': cert.date_end.strftime('%d/%m/%Y') if cert.date_end else 'N/A',
                'description': cert.description,
            }
            if cert.date_end:
                status, days_left = VehicleIssuesCheck._evaluate(cert.date_end)
                if status == 'expired':
                    cert_data['status_class'] = 'status-expired'
                    cert_data['status_text'] = 'VENCIDO'
                elif status in ['due_10', 'due_30']:
                    cert_data['status_class'] = 'status-due-10'
                    cert_data['status_text'] = f'POR VENCER ({days_left} días)'
                else:
                    cert_data['status_class'] = 'status-valid'
                    cert_data['status_text'] = 'VIGENTE'
            else:
                cert_data['status_class'] = 'status-na'
                cert_data['status_text'] = 'SIN FECHA'
            certifications_data.append(cert_data)
        
        context['certifications'] = certifications_data

        # Usuario que genera el reporte
        context['generated_by'] = self.request.user.get_full_name() or self.request.user.email

        return context
