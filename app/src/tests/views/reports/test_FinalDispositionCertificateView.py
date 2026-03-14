from datetime import date
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from projects.models.CustodyChain import CustodyChain
from projects.models.FinalDispositionCertificate import (
    FinalDispositionCertificate,
    FinalDispositionCertificateDetail,
)
from projects.models.Partner import Partner
from projects.models.Project import Project
from projects.models.SheetProject import SheetProject
from reports.views.FinalDispositionCertificate import FinalDispositionCertificateView


class FinalDispositionCertificateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_context(self, sheet_id):
        request = self.factory.get(f"/reports/template-final-disposition/{sheet_id}/")
        request.user = AnonymousUser()

        view = FinalDispositionCertificateView()
        view.request = request
        view.kwargs = {"id": sheet_id}
        return view.get_context_data()

    def _create_base_project(self, suffix="01"):
        partner = Partner.objects.create(
            business_tax_id=f"17999999{suffix:0>5}",
            name=f"Cliente {suffix}",
            address="Direccion prueba",
            email=f"cliente{suffix}@test.com",
        )
        project = Project.objects.create(
            partner=partner,
            location="Campamento Test",
            cardinal_point="NORTE",
            contact_name="Contacto Test",
            contact_phone="0999999999",
            start_date=date(2026, 1, 1),
        )
        return project

    def _create_sheet(self, project, status="IN_PROGRESS", period_day=1):
        return SheetProject.objects.create(
            project=project,
            issue_date=date(2026, 1, period_day),
            period_start=date(2026, 1, period_day),
            period_end=date(2026, 1, period_day),
            status=status,
            series_code=f"PSL-PS-2026-{1000 + period_day:04d}",
            secuence_prefix="PSL-PS",
            secuence_year=2026,
            secuence_number=1000 + period_day,
        )

    def _create_chain(self, sheet, consecutive, barrels, cubic_meters, gallons=0):
        return CustodyChain.objects.create(
            sheet_project=sheet,
            consecutive=consecutive,
            activity_date=date(2026, 1, 10),
            total_barrels=Decimal(str(barrels)),
            total_cubic_meters=Decimal(str(cubic_meters)),
            total_gallons=Decimal(str(gallons)),
        )

    def test_in_progress_persists_certificate_and_refreshes_details(self):
        """IN_PROGRESS: persiste el certificado pero refresca detalles cada vez."""
        project = self._create_base_project("11")
        sheet = self._create_sheet(project=project, status="IN_PROGRESS", period_day=11)

        self._create_chain(sheet, "0000001", "1.25", "0.20")
        self._create_chain(sheet, "0000002", "2.75", "0.80")

        context = self._build_context(sheet.id)

        # Ahora SÍ se persiste el certificado
        self.assertEqual(
            FinalDispositionCertificate.objects.filter(payment_sheet=sheet).count(),
            1,
        )
        certificate = FinalDispositionCertificate.objects.get(payment_sheet=sheet)
        self.assertTrue(certificate.nro_document.startswith("PSL-CDF-"))
        self.assertEqual(len(context["details"]), 2)
        self.assertEqual(context["total_barrels"], Decimal("4"))
        self.assertEqual(context["total_cubic_meters"], Decimal("1"))

        # Agregar una nueva cadena y verificar que los detalles se refrescan
        self._create_chain(sheet, "0000003", "5.00", "2.00")

        context2 = self._build_context(sheet.id)

        # Se mantiene un solo certificado
        self.assertEqual(
            FinalDispositionCertificate.objects.filter(payment_sheet=sheet).count(),
            1,
        )
        # Pero los detalles se actualizaron
        self.assertEqual(len(context2["details"]), 3)
        self.assertEqual(context2["total_barrels"], Decimal("9"))
        self.assertEqual(context2["total_cubic_meters"], Decimal("3"))

    def test_non_in_progress_persists_certificate_and_freezes_details(self):
        project = self._create_base_project("22")
        sheet = self._create_sheet(project=project, status="LIQUIDATED", period_day=12)

        self._create_chain(sheet, "0000001", "3.00", "1.00", gallons="132")

        context_first = self._build_context(sheet.id)

        certificate = FinalDispositionCertificate.objects.get(payment_sheet=sheet)
        self.assertTrue(certificate.nro_document.startswith("PSL-CDF-"))
        self.assertEqual(certificate.total_bbl, 3)
        self.assertEqual(certificate.total_m3, 1)
        self.assertEqual(
            FinalDispositionCertificateDetail.objects.filter(
                final_disposition_certificate=certificate
            ).count(),
            1,
        )

        # Aunque se agreguen nuevas cadenas luego de liquidar, el reporte debe quedar congelado.
        self._create_chain(sheet, "0000002", "8.00", "4.00", gallons="352")

        context_second = self._build_context(sheet.id)

        self.assertEqual(len(context_first["details"]), 1)
        self.assertEqual(len(context_second["details"]), 1)
        self.assertEqual(context_first["total_barrels"], Decimal("3"))
        self.assertEqual(context_second["total_barrels"], Decimal("3"))
        self.assertEqual(
            FinalDispositionCertificate.objects.filter(payment_sheet=sheet).count(),
            1,
        )

        sheet.refresh_from_db()
        self.assertEqual(sheet.final_disposition_reference, certificate.nro_document)

    def test_document_number_increments_by_same_day(self):
        project = self._create_base_project("33")
        sheet_one = self._create_sheet(project=project, status="LIQUIDATED", period_day=13)
        sheet_two = self._create_sheet(project=project, status="LIQUIDATED", period_day=14)

        self._create_chain(sheet_one, "0000001", "1.00", "1.00")
        self._create_chain(sheet_two, "0000002", "1.00", "1.00")

        self._build_context(sheet_one.id)
        self._build_context(sheet_two.id)

        cert_one = FinalDispositionCertificate.objects.get(payment_sheet=sheet_one)
        cert_two = FinalDispositionCertificate.objects.get(payment_sheet=sheet_two)

        self.assertEqual(cert_one.date, cert_two.date)
        self.assertEqual(cert_one.consecutive, 1)
        self.assertEqual(cert_two.consecutive, 2)
        self.assertTrue(cert_one.nro_document.endswith("-00001"))
        self.assertTrue(cert_two.nro_document.endswith("-00002"))
