import pytest
from datetime import date, timedelta
from common.TechnicalVaccinesIssuesCheck import TechnicalVaccinesIssuesCheck
from accounts.models import VaccinationRecord, Technical


@pytest.mark.django_db
class TestTechnicalVaccinesIssuesCheck:

    @pytest.fixture
    def technical(self):
        """Técnico base para los tests"""
        return Technical.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@test.com'
        )

    @pytest.fixture
    def vaccine_expired(self, technical):
        """Registro de vacuna con próxima dosis vencida"""
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=2,
            application_date=date.today() - timedelta(days=90),
            next_dose_date=date.today() - timedelta(days=5),
            is_active=True
        )

    @pytest.fixture
    def vaccine_due_10(self, technical):
        """Registro de vacuna próxima a vencer en 10 días"""
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='INFLUENZA',
            dose_number=1,
            application_date=date.today() - timedelta(days=30),
            next_dose_date=date.today() + timedelta(days=8),
            is_active=True
        )

    @pytest.fixture
    def vaccine_due_30(self, technical):
        """Registro de vacuna próxima a vencer en 30 días"""
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='HEPATITIS_B',
            dose_number=3,
            application_date=date.today() - timedelta(days=60),
            next_dose_date=date.today() + timedelta(days=25),
            is_active=True
        )

    @pytest.fixture
    def vaccine_valid(self, technical):
        """Registro de vacuna válida sin alertas"""
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='TETANUS',
            dose_number=1,
            application_date=date.today() - timedelta(days=10),
            next_dose_date=date.today() + timedelta(days=60),
            is_active=True
        )

    @pytest.fixture
    def vaccine_no_next_dose(self, technical):
        """Registro de vacuna sin próxima dosis programada"""
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=3,
            application_date=date.today() - timedelta(days=20),
            next_dose_date=None,
            is_active=True
        )

    @pytest.fixture
    def vaccine_inactive(self, technical):
        """Registro de vacuna inactiva"""
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=1,
            application_date=date.today() - timedelta(days=15),
            next_dose_date=date.today() + timedelta(days=5),
            is_active=False
        )

    @pytest.fixture
    def technical_with_multiple_vaccines(self):
        """Técnico con múltiples registros de vacunación"""
        tech = Technical.objects.create(
            first_name='María',
            last_name='González',
            email='maria.gonzalez@test.com'
        )
        
        # Vacuna vencida
        VaccinationRecord.objects.create(
            technical=tech,
            vaccine_type='COVID',
            dose_number=2,
            application_date=date.today() - timedelta(days=100),
            next_dose_date=date.today() - timedelta(days=10),
            is_active=True
        )
        
        # Vacuna próxima a vencer (10 días)
        VaccinationRecord.objects.create(
            technical=tech,
            vaccine_type='INFLUENZA',
            dose_number=1,
            application_date=date.today() - timedelta(days=20),
            next_dose_date=date.today() + timedelta(days=5),
            is_active=True
        )
        
        # Vacuna próxima a vencer (30 días)
        VaccinationRecord.objects.create(
            technical=tech,
            vaccine_type='HEPATITIS_B',
            dose_number=1,
            application_date=date.today() - timedelta(days=30),
            next_dose_date=date.today() + timedelta(days=20),
            is_active=True
        )
        
        # Vacuna válida
        VaccinationRecord.objects.create(
            technical=tech,
            vaccine_type='TETANUS',
            dose_number=1,
            application_date=date.today() - timedelta(days=10),
            next_dose_date=date.today() + timedelta(days=90),
            is_active=True
        )
        
        # Vacuna sin próxima dosis
        VaccinationRecord.objects.create(
            technical=tech,
            vaccine_type='YELLOW_FEVER',
            dose_number=1,
            application_date=date.today() - timedelta(days=40),
            next_dose_date=None,
            is_active=True
        )
        
        return tech

    def test_evaluate_expired_date(self):
        """Test que _evaluate detecta fechas vencidas"""
        expired_date = date.today() - timedelta(days=5)
        status, days = TechnicalVaccinesIssuesCheck._evaluate(expired_date)
        
        assert status == 'expired'
        assert days == -5

    def test_evaluate_due_10_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (10 días)"""
        due_date = date.today() + timedelta(days=8)
        status, days = TechnicalVaccinesIssuesCheck._evaluate(due_date)
        
        assert status == 'due_10'
        assert days == 8

    def test_evaluate_due_30_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (30 días)"""
        due_date = date.today() + timedelta(days=25)
        status, days = TechnicalVaccinesIssuesCheck._evaluate(due_date)
        
        assert status == 'due_30'
        assert days == 25

    def test_evaluate_valid_date(self):
        """Test que _evaluate retorna None para fechas válidas"""
        valid_date = date.today() + timedelta(days=60)
        status, days = TechnicalVaccinesIssuesCheck._evaluate(valid_date)
        
        assert status is None
        assert days is None

    def test_evaluate_none_date(self):
        """Test que _evaluate maneja correctamente fechas None"""
        status, days = TechnicalVaccinesIssuesCheck._evaluate(None)
        
        assert status is None
        assert days is None

    def test_issues_for_expired_vaccine(self, technical, vaccine_expired):
        """Test de issues_for con vacuna vencida"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'next_dose_date'
        assert 'Vacuna' in issues[0]['label']
        assert 'Dosis 2' in issues[0]['label']
        assert issues[0]['status'] == 'expired'
        assert issues[0]['days_left'] == -5
        assert issues[0]['vaccination_record_id'] == vaccine_expired.id
        assert issues[0]['technical_id'] == technical.id
        assert issues[0]['technical_name'] == 'Juan Pérez'
        assert issues[0]['vaccine_type'] == 'COVID'

    def test_issues_for_due_10_vaccine(self, technical, vaccine_due_10):
        """Test de issues_for con vacuna próxima a vencer (10 días)"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'next_dose_date'
        assert issues[0]['status'] == 'due_10'
        assert issues[0]['days_left'] == 8
        assert issues[0]['vaccine_type'] == 'INFLUENZA'

    def test_issues_for_due_30_vaccine(self, technical, vaccine_due_30):
        """Test de issues_for con vacuna próxima a vencer (30 días)"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'next_dose_date'
        assert issues[0]['status'] == 'due_30'
        assert issues[0]['days_left'] == 25
        assert issues[0]['vaccine_type'] == 'HEPATITIS_B'

    def test_issues_for_valid_vaccine(self, technical, vaccine_valid):
        """Test de issues_for con vacuna válida sin alertas"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 0

    def test_issues_for_vaccine_no_next_dose(self, technical, vaccine_no_next_dose):
        """Test de issues_for con vacuna sin próxima dosis programada"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 0

    def test_issues_for_vaccine_inactive(self, technical, vaccine_inactive):
        """Test de issues_for no incluye vacunas inactivas"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 0

    def test_issues_for_technical_with_multiple_vaccines(self, technical_with_multiple_vaccines):
        """Test de issues_for con técnico con múltiples vacunas"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical_with_multiple_vaccines)
        
        # Deben haber 3 issues (vencida, due_10, due_30)
        assert len(issues) == 3
        
        # Verificar estados
        statuses = [issue['status'] for issue in issues]
        assert 'expired' in statuses
        assert 'due_10' in statuses
        assert 'due_30' in statuses

    def test_issues_all_multiple_technicals(
        self,
        technical,
        vaccine_expired,
        vaccine_due_10
    ):
        """Test de issues_all con múltiples técnicos"""
        # Crear otro técnico con vacuna
        tech2 = Technical.objects.create(
            first_name='Carlos',
            last_name='López',
            email='carlos@test.com'
        )
        vaccine2 = VaccinationRecord.objects.create(
            technical=tech2,
            vaccine_type='COVID',
            dose_number=1,
            application_date=date.today() - timedelta(days=20),
            next_dose_date=date.today() + timedelta(days=5),
            is_active=True
        )
        
        issues = TechnicalVaccinesIssuesCheck.issues_all()
        
        # Filtrar solo los issues de los técnicos creados en este test
        test_technical_ids = [technical.id, tech2.id]
        test_issues = [issue for issue in issues if issue['technical_id'] in test_technical_ids]
        
        # Deben haber 3 issues totales
        assert len(test_issues) == 3
        
        # Verificar que ambos técnicos están representados
        technical_ids = [issue['technical_id'] for issue in test_issues]
        assert technical.id in technical_ids
        assert tech2.id in technical_ids

    def test_issues_all_with_queryset(self, technical, vaccine_expired):
        """Test de issues_all con queryset específico"""
        # Crear otro técnico que no debe incluirse
        tech2 = Technical.objects.create(
            first_name='Ana',
            last_name='Martínez',
            email='ana@test.com'
        )
        VaccinationRecord.objects.create(
            technical=tech2,
            vaccine_type='COVID',
            dose_number=1,
            application_date=date.today() - timedelta(days=10),
            next_dose_date=date.today() - timedelta(days=3),
            is_active=True
        )
        
        # Filtrar solo el primer técnico
        queryset = Technical.objects.filter(id=technical.id)
        issues = TechnicalVaccinesIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 1
        assert issues[0]['technical_id'] == technical.id

    def test_issues_all_empty_queryset(self):
        """Test de issues_all con queryset vacío"""
        queryset = Technical.objects.none()
        issues = TechnicalVaccinesIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 0

    def test_warning_constants(self):
        """Test que las constantes de advertencia están correctamente definidas"""
        assert TechnicalVaccinesIssuesCheck.WARNING_30 == 30
        assert TechnicalVaccinesIssuesCheck.WARNING_10 == 10

    def test_issue_structure_complete(self, technical, vaccine_expired):
        """Test que la estructura de un issue contiene todos los campos necesarios"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) > 0
        issue = issues[0]
        
        required_keys = [
            'field', 'label', 'status', 'days_left',
            'expires_on', 'vaccination_record_id', 'technical_id',
            'technical_name', 'vaccine_type'
        ]
        
        for key in required_keys:
            assert key in issue

    def test_technical_name_format(self, technical, vaccine_expired):
        """Test que el nombre del técnico se formatea correctamente"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert issues[0]['technical_name'] == 'Juan Pérez'
        assert issues[0]['technical_name'] == f"{technical.first_name} {technical.last_name}"

    def test_expires_on_field(self, technical, vaccine_expired):
        """Test que el campo expires_on contiene la fecha correcta"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert issues[0]['expires_on'] == vaccine_expired.next_dose_date

    def test_vaccination_record_id_field(self, technical, vaccine_expired):
        """Test que el campo vaccination_record_id está presente y es correcto"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert issues[0]['vaccination_record_id'] == vaccine_expired.id

    def test_vaccine_type_field(self, technical, vaccine_expired):
        """Test que el campo vaccine_type está presente y es correcto"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert issues[0]['vaccine_type'] == vaccine_expired.vaccine_type

    def test_label_format_with_dose_number(self, technical, vaccine_expired):
        """Test que el label incluye el tipo de vacuna y número de dosis"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        label = issues[0]['label']
        assert 'Vacuna' in label
        assert vaccine_expired.get_vaccine_type_display() in label
        assert f"Dosis {vaccine_expired.dose_number}" in label

    def test_label_format_without_dose_number(self, technical):
        """Test que el label maneja correctamente cuando dose_number es None"""
        vaccine = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=None,
            application_date=date.today() - timedelta(days=10),
            next_dose_date=date.today() - timedelta(days=5),
            is_active=True
        )
        
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 1
        assert 'Dosis N/A' in issues[0]['label']

    def test_boundary_condition_exactly_10_days(self):
        """Test de condición límite: exactamente 10 días"""
        exactly_10_days = date.today() + timedelta(days=10)
        status, days = TechnicalVaccinesIssuesCheck._evaluate(exactly_10_days)
        
        assert status == 'due_10'
        assert days == 10

    def test_boundary_condition_exactly_30_days(self):
        """Test de condición límite: exactamente 30 días"""
        exactly_30_days = date.today() + timedelta(days=30)
        status, days = TechnicalVaccinesIssuesCheck._evaluate(exactly_30_days)
        
        assert status == 'due_30'
        assert days == 30

    def test_boundary_condition_31_days(self):
        """Test de condición límite: 31 días (sin alerta)"""
        exactly_31_days = date.today() + timedelta(days=31)
        status, days = TechnicalVaccinesIssuesCheck._evaluate(exactly_31_days)
        
        assert status is None
        assert days is None

    def test_boundary_condition_exactly_0_days(self):
        """Test de condición límite: exactamente hoy (día 0)"""
        today = date.today()
        status, days = TechnicalVaccinesIssuesCheck._evaluate(today)
        
        assert status == 'due_10'
        assert days == 0

    def test_issues_all_sorting(self, technical):
        """Test que los issues se pueden ordenar por días restantes"""
        # Crear vacunas con diferentes fechas
        v1 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=1,
            application_date=date.today() - timedelta(days=90),
            next_dose_date=date.today() - timedelta(days=5),
            is_active=True
        )
        v2 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='INFLUENZA',
            dose_number=1,
            application_date=date.today() - timedelta(days=60),
            next_dose_date=date.today() + timedelta(days=2),
            is_active=True
        )
        v3 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='HEPATITIS_B',
            dose_number=1,
            application_date=date.today() - timedelta(days=30),
            next_dose_date=date.today() + timedelta(days=20),
            is_active=True
        )
        
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        # Verificar que hay 3 issues
        assert len(issues) == 3
        
        # Ordenar por días restantes
        sorted_issues = sorted(issues, key=lambda x: x['days_left'])
        
        # El primero debe ser el vencido (días negativos)
        assert sorted_issues[0]['days_left'] < 0
        assert sorted_issues[0]['status'] == 'expired'

    def test_multiple_vaccines_same_type_different_doses(self, technical):
        """Test con múltiples vacunas del mismo tipo pero diferentes dosis"""
        # Dosis 1 vencida
        VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=1,
            application_date=date.today() - timedelta(days=100),
            next_dose_date=date.today() - timedelta(days=10),
            is_active=True
        )
        
        # Dosis 2 próxima a vencer
        VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=2,
            application_date=date.today() - timedelta(days=50),
            next_dose_date=date.today() + timedelta(days=5),
            is_active=True
        )
        
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        # Deben haber 2 issues
        assert len(issues) == 2
        
        # Verificar que ambas dosis están representadas
        labels = [issue['label'] for issue in issues]
        assert any('Dosis 1' in label for label in labels)
        assert any('Dosis 2' in label for label in labels)

    def test_only_active_vaccination_records(self, technical):
        """Test que solo se consideran registros activos"""
        # Vacuna activa vencida
        VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            dose_number=1,
            application_date=date.today() - timedelta(days=90),
            next_dose_date=date.today() - timedelta(days=5),
            is_active=True
        )
        
        # Vacuna inactiva vencida (no debe aparecer)
        VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='INFLUENZA',
            dose_number=1,
            application_date=date.today() - timedelta(days=100),
            next_dose_date=date.today() - timedelta(days=10),
            is_active=False
        )
        
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        # Solo debe haber 1 issue (la activa)
        assert len(issues) == 1
        assert issues[0]['vaccine_type'] == 'COVID'

    def test_technical_without_vaccination_records(self, technical):
        """Test con técnico sin registros de vacunación"""
        issues = TechnicalVaccinesIssuesCheck.issues_for(technical)
        
        assert len(issues) == 0

    def test_issues_all_no_technicals(self):
        """Test de issues_all con queryset vacío"""
        queryset = Technical.objects.none()
        issues = TechnicalVaccinesIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 0
