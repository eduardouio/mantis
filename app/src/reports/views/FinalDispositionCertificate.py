from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from common.AppLoggin import loggin_event
from projects.models.CustodyChain import CustodyChain
from projects.models.SheetProject import SheetProject
from projects.models.FinalDispositionCertificate import (
    FinalDispositionCertificate,
    FinalDispositionCertificateDetail,
)


class FinalDispositionCertificateView(TemplateView):
    template_name = "reports/final_disposition_certificate.html"
    DOCUMENT_PREFIX = "PSL-CDF"
    DEFAULT_REFERENCE_NUMBER = "PSL-CDF-00000000-00000"

    @staticmethod
    def _to_decimal(value):
        if value is None:
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def _get_sheet_custody_chains(self, sheet_project):
        return CustodyChain.objects.filter(
            sheet_project=sheet_project,
            is_deleted=False,
        ).order_by("activity_date", "id")

    def _get_next_document_data(self, issue_date):
        last_certificate = (
            FinalDispositionCertificate.objects.select_for_update()
            .filter(
                date=issue_date,
                is_deleted=False,
            )
            .order_by("-consecutive", "-id")
            .first()
        )

        next_consecutive = (last_certificate.consecutive + 1) if last_certificate else 1
        document_number = (
            f"{self.DOCUMENT_PREFIX}-{issue_date.strftime('%Y%m%d')}-{next_consecutive:05d}"
        )
        return next_consecutive, document_number

    def _sync_certificate_details(self, certificate, sheet_project):
        """Recrea los detalles del certificado a partir de las cadenas de custodia actuales."""
        FinalDispositionCertificateDetail.objects.filter(
            final_disposition_certificate=certificate,
        ).delete()

        total_bbl = Decimal("0")
        total_gallons = Decimal("0")
        total_m3 = Decimal("0")
        detail_rows = []

        for chain in self._get_sheet_custody_chains(sheet_project):
            q_bbl = self._to_decimal(chain.total_barrels)
            q_gallons = self._to_decimal(chain.total_gallons)
            q_m3 = self._to_decimal(chain.total_cubic_meters)

            detail_rows.append(
                FinalDispositionCertificateDetail(
                    final_disposition_certificate=certificate,
                    custody_chain=chain,
                    date=chain.activity_date,
                    descritpion="AGUAS NEGRAS Y GRISES",
                    treatment_type="TB3",
                    detail="AGUAS NEGRAS Y GRISES",
                    quantity_bbl=q_bbl,
                    quantity_gallons=q_gallons,
                    quantity_m3=q_m3,
                )
            )

            total_bbl += q_bbl
            total_gallons += q_gallons
            total_m3 += q_m3

        if detail_rows:
            FinalDispositionCertificateDetail.objects.bulk_create(detail_rows)

        certificate.total_bbl = int(total_bbl.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        certificate.total_gallons = int(total_gallons.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        certificate.total_m3 = int(total_m3.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        certificate.save()

    def _create_certificate(self, sheet_project):
        """Crea el certificado con número de documento y cabeceras."""
        issue_date = date.today()
        next_consecutive, document_number = self._get_next_document_data(issue_date)

        project = sheet_project.project
        partner = project.partner
        location = f"{project.location or ''} {project.cardinal_point or ''}".strip()

        certificate = FinalDispositionCertificate.objects.create(
            payment_sheet=sheet_project,
            nro_document=document_number,
            consecutive=next_consecutive,
            date=issue_date,
            customer=partner.name,
            customer_ruc=partner.business_tax_id,
            location=location,
            text_document="CERTIFICADO DE TRATAMIENTO Y DISPOSICION FINAL",
            total_bbl=0,
            total_gallons=0,
            total_m3=0,
        )

        self._sync_certificate_details(certificate, sheet_project)

        sheet_project.final_disposition_reference = document_number
        sheet_project.save()

        return certificate

    def _get_or_create_certificate(self, sheet_project):
        """Obtiene o crea el certificado. Si IN_PROGRESS, refresca los detalles."""
        with transaction.atomic():
            certificate = (
                FinalDispositionCertificate.objects.select_for_update()
                .filter(
                    payment_sheet=sheet_project,
                    is_deleted=False,
                )
                .order_by("id")
                .first()
            )

            if certificate:
                if sheet_project.status == "IN_PROGRESS":
                    self._sync_certificate_details(certificate, sheet_project)
                return certificate

            return self._create_certificate(sheet_project)

    def _build_details_from_certificate(self, certificate):
        details = []
        certificate_details = FinalDispositionCertificateDetail.objects.filter(
            final_disposition_certificate=certificate,
            is_deleted=False,
        ).order_by("date", "id")

        for item in certificate_details:
            details.append({
                "date": item.date,
                "residue_description": item.descritpion or "AGUAS NEGRAS Y GRISES",
                "custody_chain_number": item.custody_chain.consecutive if item.custody_chain_id else "",
                "treatment_type": item.treatment_type or "TB3",
                "barrels": item.quantity_bbl,
                "cubic_meters": item.quantity_m3,
            })

        return details

    def get_context_data(self, **kwargs):
        loggin_event("Mostrando certificado de disposición final")
        context = super().get_context_data(**kwargs)

        sheet_project_id = self.kwargs.get('id')

        if not sheet_project_id:
            context.update({
                "certificate": {"reference_number": self.DEFAULT_REFERENCE_NUMBER},
                "partner": {"name": "", "ruc": ""},
                "project": {"name": "", "location": ""},
                "details": [],
                "total_barrels": 0,
                "total_cubic_meters": 0,
            })
            return context

        sheet_project = get_object_or_404(SheetProject, id=sheet_project_id)
        project = sheet_project.project
        partner = project.partner

        certificate = self._get_or_create_certificate(sheet_project)
        details = self._build_details_from_certificate(certificate)
        total_barrels = self._to_decimal(certificate.total_bbl)
        total_cubic_meters = self._to_decimal(certificate.total_m3)
        reference_number = certificate.nro_document or self.DEFAULT_REFERENCE_NUMBER

        context.update({
            "certificate": {
                "reference_number": reference_number,
            },
            "partner": {
                "name": partner.name,
                "ruc": partner.business_tax_id,
            },
            "project": {
                "name": partner.name,
                "location": f"{project.location or ''} {project.cardinal_point or ''}".strip(),
            },
            "details": details,
            "total_barrels": total_barrels,
            "total_cubic_meters": total_cubic_meters,
        })

        if self.request.user.is_authenticated:
            context['siganture_name'] = self.request.user.siganture_name or ''
            context['siganture_role'] = self.request.user.siganture_role or ''

        return context
