import pytest
from datetime import date, timedelta
from accounts.models.VaccinationRecord import VaccinationRecord
from accounts.models.Technical import Technical


@pytest.mark.django_db
class TestVaccinationRecord:
    
    def test_create_vaccination_record(self):
        technical = Technical.objects.create(
            first_name='Juan',
            last_name='Pérez',
            dni='1234567890',
            nro_phone='0987654321'
        )
        vaccination = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            batch_number='COV-001',
            application_date=date(2024, 6, 1),
            next_dose_date=date(2024, 12, 1)
        )
        assert vaccination.technical == technical
        assert vaccination.vaccine_type == 'COVID'
        assert vaccination.batch_number == 'COV-001'
        assert vaccination.application_date == date(2024, 6, 1)
        assert vaccination.next_dose_date == date(2024, 12, 1)

    def test_vaccination_record_str(self):
        technical = Technical.objects.create(
            first_name='María',
            last_name='González',
            dni='0987654321',
            nro_phone='0999888777'
        )
        vaccination = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='HEPATITIS_A_B',
            application_date=date(2024, 3, 15)
        )
        expected_str = f'{technical} - Hepatitis A y B ({date(2024, 3, 15)})'
        assert str(vaccination) == expected_str

    def test_days_to_next_dose_property(self):
        technical = Technical.objects.create(
            first_name='Carlos',
            last_name='Rodríguez',
            dni='1122334455',
            nro_phone='0966555444'
        )
        vaccination = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='TETANUS',
            application_date=date(2024, 1, 1),
            next_dose_date=date(2024, 1, 31)
        )
        expected_days = 30  # 31 - 1 = 30 days
        assert vaccination.days_to_next_dose == expected_days

    def test_days_to_next_dose_no_next_dose(self):
        technical = Technical.objects.create(
            first_name='Ana',
            last_name='López',
            dni='5566778899',
            nro_phone='0955444333'
        )
        vaccination = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='INFLUENZA',
            application_date=date(2024, 6, 1)
            # No next_dose_date
        )
        assert vaccination.days_to_next_dose == 0

    def test_get_all_by_technical(self):
        technical = Technical.objects.create(
            first_name='Pedro',
            last_name='Martínez',
            dni='9988776655',
            nro_phone='0944333222'
        )
        
        # Create multiple vaccination records
        vac1 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            application_date=date(2024, 1, 1),
            is_active=True
        )
        vac2 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='TETANUS',
            application_date=date(2024, 6, 1),
            is_active=True
        )
        vac3 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='INFLUENZA',
            application_date=date(2024, 3, 1),
            is_active=False  # Inactive
        )
        
        records = VaccinationRecord.get_all_by_technical(technical.id)
        assert len(records) == 2  # Only active records
        assert list(records) == [vac2, vac1]  # Ordered by -application_date

    def test_vaccine_type_choices(self):
        technical = Technical.objects.create(
            first_name='Luis',
            last_name='Fernández',
            dni='1111222333',
            nro_phone='0933222111'
        )
        
        for vaccine_code, _ in VaccinationRecord.VACCINE_TYPE_CHOICES:
            vaccination = VaccinationRecord.objects.create(
                technical=technical,
                vaccine_type=vaccine_code,
                application_date=date(2024, 6, 1)
            )
            assert vaccination.vaccine_type == vaccine_code
            vaccination.delete()  # Clean up
