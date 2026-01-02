import pytest
from datetime import date, timedelta
from common.TechnicalIssuesCheck import TechnicalIssuesCheck
from accounts.models import Technical


@pytest.mark.django_db
class TestTechnicalIssuesCheck:

    @pytest.fixture
    def technical_with_expired_license(self):
        """Técnico con licencia vencida"""
        technical = Technical.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@test.com',
            license_expiry_date=date.today() - timedelta(days=5)
        )
        return technical

    @pytest.fixture
    def technical_with_due_10_certificate(self):
        """Técnico con certificado próximo a vencer (10 días)"""
        technical = Technical.objects.create(
            first_name='María',
            last_name='González',
            email='maria.gonzalez@test.com',
            medical_certificate_expiry_date=date.today() + timedelta(days=8)
        )
        return technical

    @pytest.fixture
    def technical_with_due_30_certificate(self):
        """Técnico con certificado próximo a vencer (30 días)"""
        technical = Technical.objects.create(
            first_name='Carlos',
            last_name='López',
            email='carlos.lopez@test.com',
            defensive_driving_certificate_expiry_date=date.today() + timedelta(days=25)
        )
        return technical

    @pytest.fixture
    def technical_with_valid_certificates(self):
        """Técnico con todos los certificados válidos"""
        technical = Technical.objects.create(
            first_name='Ana',
            last_name='Martínez',
            email='ana.martinez@test.com',
            license_expiry_date=date.today() + timedelta(days=90),
            medical_certificate_expiry_date=date.today() + timedelta(days=60),
            mae_certificate_expiry_date=date.today() + timedelta(days=45)
        )
        return technical

    @pytest.fixture
    def technical_with_multiple_issues(self):
        """Técnico con múltiples problemas"""
        technical = Technical.objects.create(
            first_name='Pedro',
            last_name='Ramírez',
            email='pedro.ramirez@test.com',
            license_expiry_date=date.today() - timedelta(days=10),
            medical_certificate_expiry_date=date.today() + timedelta(days=5),
            quest_end_date=date.today() + timedelta(days=20)
        )
        return technical

    def test_evaluate_expired_date(self):
        """Test que _evaluate detecta fechas vencidas"""
        expired_date = date.today() - timedelta(days=5)
        status, days = TechnicalIssuesCheck._evaluate(expired_date)
        
        assert status == 'expired'
        assert days == -5

    def test_evaluate_due_10_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (10 días)"""
        due_date = date.today() + timedelta(days=8)
        status, days = TechnicalIssuesCheck._evaluate(due_date)
        
        assert status == 'due_10'
        assert days == 8

    def test_evaluate_due_30_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (30 días)"""
        due_date = date.today() + timedelta(days=25)
        status, days = TechnicalIssuesCheck._evaluate(due_date)
        
        assert status == 'due_30'
        assert days == 25

    def test_evaluate_valid_date(self):
        """Test que _evaluate retorna None para fechas válidas"""
        valid_date = date.today() + timedelta(days=60)
        status, days = TechnicalIssuesCheck._evaluate(valid_date)
        
        assert status is None
        assert days is None

    def test_evaluate_none_date(self):
        """Test que _evaluate maneja correctamente fechas None"""
        status, days = TechnicalIssuesCheck._evaluate(None)
        
        assert status is None
        assert days is None

    def test_issues_for_expired_license(self, technical_with_expired_license):
        """Test de issues_for con licencia vencida"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_expired_license)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'license_expiry_date'
        assert issues[0]['label'] == 'Licencia de conducir'
        assert issues[0]['status'] == 'expired'
        assert issues[0]['days_left'] == -5
        assert issues[0]['technical_id'] == technical_with_expired_license.id
        assert issues[0]['technical_name'] == 'Juan Pérez'

    def test_issues_for_due_10_certificate(self, technical_with_due_10_certificate):
        """Test de issues_for con certificado próximo a vencer (10 días)"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_due_10_certificate)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'medical_certificate_expiry_date'
        assert issues[0]['label'] == 'Certificado médico'
        assert issues[0]['status'] == 'due_10'
        assert issues[0]['days_left'] == 8

    def test_issues_for_due_30_certificate(self, technical_with_due_30_certificate):
        """Test de issues_for con certificado próximo a vencer (30 días)"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_due_30_certificate)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'defensive_driving_certificate_expiry_date'
        assert issues[0]['label'] == 'Certificado de manejo defensivo'
        assert issues[0]['status'] == 'due_30'
        assert issues[0]['days_left'] == 25

    def test_issues_for_valid_certificates(self, technical_with_valid_certificates):
        """Test de issues_for sin problemas"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_valid_certificates)
        
        assert len(issues) == 0

    def test_issues_for_multiple_issues(self, technical_with_multiple_issues):
        """Test de issues_for con múltiples problemas"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_multiple_issues)
        
        assert len(issues) == 3
        
        # Verificar que todos los issues tienen la estructura correcta
        for issue in issues:
            assert 'field' in issue
            assert 'label' in issue
            assert 'status' in issue
            assert 'days_left' in issue
            assert 'expires_on' in issue
            assert 'technical_id' in issue
            assert 'technical_name' in issue
        
        # Verificar estados específicos
        statuses = [issue['status'] for issue in issues]
        assert 'expired' in statuses
        assert 'due_10' in statuses
        assert 'due_30' in statuses

    def test_issues_all_multiple_technicals(
        self,
        technical_with_expired_license,
        technical_with_due_10_certificate,
        technical_with_valid_certificates
    ):
        """Test de issues_all con múltiples técnicos"""
        issues = TechnicalIssuesCheck.issues_all()
        
        # Filtrar solo los issues de los técnicos creados en este test
        test_technical_ids = [
            technical_with_expired_license.id,
            technical_with_due_10_certificate.id,
            technical_with_valid_certificates.id
        ]
        test_issues = [issue for issue in issues if issue['technical_id'] in test_technical_ids]
        
        # Deben haber 2 issues en total (uno del técnico con licencia vencida
        # y uno del técnico con certificado próximo a vencer)
        assert len(test_issues) == 2
        
        # Verificar que los técnicos están representados
        technical_ids = [issue['technical_id'] for issue in test_issues]
        assert technical_with_expired_license.id in technical_ids
        assert technical_with_due_10_certificate.id in technical_ids
        assert technical_with_valid_certificates.id not in technical_ids

    def test_issues_all_with_queryset(
        self,
        technical_with_expired_license,
        technical_with_due_10_certificate
    ):
        """Test de issues_all con queryset específico"""
        queryset = Technical.objects.filter(
            id=technical_with_expired_license.id
        )
        issues = TechnicalIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 1
        assert issues[0]['technical_id'] == technical_with_expired_license.id

    def test_issues_all_empty_queryset(self):
        """Test de issues_all con queryset vacío"""
        queryset = Technical.objects.none()
        issues = TechnicalIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 0

    def test_field_labels_complete(self):
        """Test que todos los campos tienen etiquetas definidas"""
        expected_fields = [
            'license_expiry_date',
            'defensive_driving_certificate_expiry_date',
            'mae_certificate_expiry_date',
            'medical_certificate_expiry_date',
            'quest_end_date'
        ]
        
        for field in expected_fields:
            assert field in TechnicalIssuesCheck.FIELD_LABELS
            assert TechnicalIssuesCheck.FIELD_LABELS[field]

    def test_warning_constants(self):
        """Test que las constantes de advertencia están correctamente definidas"""
        assert TechnicalIssuesCheck.WARNING_30 == 30
        assert TechnicalIssuesCheck.WARNING_10 == 10

    def test_issue_structure_complete(self, technical_with_expired_license):
        """Test que la estructura de un issue contiene todos los campos necesarios"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_expired_license)
        
        assert len(issues) > 0
        issue = issues[0]
        
        required_keys = [
            'field', 'label', 'status', 'days_left',
            'expires_on', 'technical_id', 'technical_name'
        ]
        
        for key in required_keys:
            assert key in issue

    def test_technical_name_format(self, technical_with_expired_license):
        """Test que el nombre del técnico se formatea correctamente"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_expired_license)
        
        assert issues[0]['technical_name'] == 'Juan Pérez'
        assert issues[0]['technical_name'] == f"{technical_with_expired_license.first_name} {technical_with_expired_license.last_name}"

    def test_expires_on_field(self, technical_with_expired_license):
        """Test que el campo expires_on contiene la fecha correcta"""
        issues = TechnicalIssuesCheck.issues_for(technical_with_expired_license)
        
        assert issues[0]['expires_on'] == technical_with_expired_license.license_expiry_date

    def test_boundary_condition_exactly_10_days(self):
        """Test de condición límite: exactamente 10 días"""
        exactly_10_days = date.today() + timedelta(days=10)
        status, days = TechnicalIssuesCheck._evaluate(exactly_10_days)
        
        assert status == 'due_10'
        assert days == 10

    def test_boundary_condition_exactly_30_days(self):
        """Test de condición límite: exactamente 30 días"""
        exactly_30_days = date.today() + timedelta(days=30)
        status, days = TechnicalIssuesCheck._evaluate(exactly_30_days)
        
        assert status == 'due_30'
        assert days == 30

    def test_boundary_condition_31_days(self):
        """Test de condición límite: 31 días (sin alerta)"""
        exactly_31_days = date.today() + timedelta(days=31)
        status, days = TechnicalIssuesCheck._evaluate(exactly_31_days)
        
        assert status is None
        assert days is None
