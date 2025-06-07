import pytest
from datetime import date
from accounts.models.Technical import Technical


@pytest.mark.django_db
class TestTechnical:
    
    def test_create_technical(self):
        technical = Technical.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@example.com',
            work_area='ASSISTANT',
            dni='1234567890',
            nro_phone='0987654321'
        )
        assert technical.first_name == 'Juan'
        assert technical.last_name == 'Pérez'
        assert technical.email == 'juan.perez@example.com'
        assert technical.work_area == 'ASSISTANT'
        assert technical.dni == '1234567890'
        assert not technical.is_active  # default False

    def test_technical_work_areas(self):
        technical = Technical.objects.create(
            first_name='María',
            last_name='González',
            work_area='SUPERVISOR',
            dni='0987654321',
            nro_phone='0999888777'
        )
        assert technical.work_area == 'SUPERVISOR'

    def test_technical_certificates(self):
        technical = Technical.objects.create(
            first_name='Carlos',
            last_name='Rodríguez',
            dni='1122334455',
            nro_phone='0966555444',
            license_issue_date=date(2023, 1, 15),
            license_expiry_date=date(2028, 1, 15),
            medical_certificate_issue_date=date(2024, 6, 1),
            medical_certificate_expiry_date=date(2025, 6, 1)
        )
        assert technical.license_issue_date == date(2023, 1, 15)
        assert technical.license_expiry_date == date(2028, 1, 15)
        assert technical.medical_certificate_issue_date == date(2024, 6, 1)

    def test_technical_insurance_flags(self):
        technical = Technical.objects.create(
            first_name='Ana',
            last_name='López',
            dni='5566778899',
            nro_phone='0955444333',
            is_iess_affiliated=True,
            has_life_insurance_policy=True,
            is_active=True
        )
        assert technical.is_iess_affiliated
        assert technical.has_life_insurance_policy
        assert technical.is_active

    def test_technical_quest_certification(self):
        technical = Technical.objects.create(
            first_name='Pedro',
            last_name='Martínez',
            dni='9988776655',
            nro_phone='0944333222',
            quest_ncst_code='QUEST-001',
            quest_instructor='Instructor ABC',
            quest_start_date=date(2024, 1, 1),
            quest_end_date=date(2024, 12, 31)
        )
        assert technical.quest_ncst_code == 'QUEST-001'
        assert technical.quest_instructor == 'Instructor ABC'
        assert technical.quest_start_date == date(2024, 1, 1)
        assert technical.quest_end_date == date(2024, 12, 31)