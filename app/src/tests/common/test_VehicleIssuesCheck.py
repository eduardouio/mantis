import pytest
from datetime import date, timedelta
from common.VehicleIssuesCheck import VehicleIssuesCheck
from equipment.models import Vehicle


@pytest.mark.django_db
class TestVehicleIssuesCheck:

    @pytest.fixture
    def vehicle_with_expired_cert(self):
        """Vehículo con certificado de operación vencido"""
        return Vehicle.objects.create(
            no_plate='ABC-1234',
            brand='Toyota',
            model='Hilux',
            year=2020,
            due_date_cert_oper=date.today() - timedelta(days=5)
        )

    @pytest.fixture
    def vehicle_with_due_10_matricula(self):
        """Vehículo con matrícula próxima a vencer (10 días)"""
        return Vehicle.objects.create(
            no_plate='XYZ-5678',
            brand='Chevrolet',
            model='D-Max',
            year=2021,
            due_date_matricula=date.today() + timedelta(days=8)
        )

    @pytest.fixture
    def vehicle_with_due_30_insurance(self):
        """Vehículo con seguro próximo a vencer (30 días)"""
        return Vehicle.objects.create(
            no_plate='DEF-9012',
            brand='Ford',
            model='Ranger',
            year=2019,
            insurance_expiration_date=date.today() + timedelta(days=25)
        )

    @pytest.fixture
    def vehicle_with_valid_dates(self):
        """Vehículo con todas las fechas válidas"""
        return Vehicle.objects.create(
            no_plate='GHI-3456',
            brand='Nissan',
            model='Frontier',
            year=2022,
            due_date_cert_oper=date.today() + timedelta(days=90),
            due_date_matricula=date.today() + timedelta(days=60),
            due_date_mtop=date.today() + timedelta(days=45),
            due_date_technical_review=date.today() + timedelta(days=70),
            insurance_expiration_date=date.today() + timedelta(days=80),
            due_date_satellite=date.today() + timedelta(days=50)
        )

    @pytest.fixture
    def vehicle_with_multiple_issues(self):
        """Vehículo con múltiples problemas"""
        return Vehicle.objects.create(
            no_plate='JKL-7890',
            brand='Mitsubishi',
            model='L200',
            year=2018,
            due_date_cert_oper=date.today() - timedelta(days=10),
            due_date_matricula=date.today() + timedelta(days=5),
            insurance_expiration_date=date.today() + timedelta(days=20)
        )

    def test_evaluate_expired_date(self):
        """Test que _evaluate detecta fechas vencidas"""
        expired_date = date.today() - timedelta(days=5)
        status, days = VehicleIssuesCheck._evaluate(expired_date)
        
        assert status == 'expired'
        assert days == -5

    def test_evaluate_due_10_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (10 días)"""
        due_date = date.today() + timedelta(days=8)
        status, days = VehicleIssuesCheck._evaluate(due_date)
        
        assert status == 'due_10'
        assert days == 8

    def test_evaluate_due_30_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (30 días)"""
        due_date = date.today() + timedelta(days=25)
        status, days = VehicleIssuesCheck._evaluate(due_date)
        
        assert status == 'due_30'
        assert days == 25

    def test_evaluate_valid_date(self):
        """Test que _evaluate retorna None para fechas válidas"""
        valid_date = date.today() + timedelta(days=60)
        status, days = VehicleIssuesCheck._evaluate(valid_date)
        
        assert status is None
        assert days is None

    def test_evaluate_none_date(self):
        """Test que _evaluate maneja correctamente fechas None"""
        status, days = VehicleIssuesCheck._evaluate(None)
        
        assert status is None
        assert days is None

    def test_issues_for_expired_cert(self, vehicle_with_expired_cert):
        """Test de issues_for con certificado vencido"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_expired_cert)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'due_date_cert_oper'
        assert issues[0]['label'] == 'Certificado de Operación'
        assert issues[0]['status'] == 'expired'
        assert issues[0]['days_left'] == -5
        assert issues[0]['vehicle_id'] == vehicle_with_expired_cert.id
        assert issues[0]['vehicle_plate'] == 'ABC-1234'

    def test_issues_for_due_10_matricula(self, vehicle_with_due_10_matricula):
        """Test de issues_for con matrícula próxima a vencer (10 días)"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_due_10_matricula)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'due_date_matricula'
        assert issues[0]['label'] == 'Matrícula'
        assert issues[0]['status'] == 'due_10'
        assert issues[0]['days_left'] == 8

    def test_issues_for_due_30_insurance(self, vehicle_with_due_30_insurance):
        """Test de issues_for con seguro próximo a vencer (30 días)"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_due_30_insurance)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'insurance_expiration_date'
        assert issues[0]['label'] == 'Seguro'
        assert issues[0]['status'] == 'due_30'
        assert issues[0]['days_left'] == 25

    def test_issues_for_valid_dates(self, vehicle_with_valid_dates):
        """Test de issues_for sin problemas"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_valid_dates)
        
        assert len(issues) == 0

    def test_issues_for_multiple_issues(self, vehicle_with_multiple_issues):
        """Test de issues_for con múltiples problemas"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_multiple_issues)
        
        assert len(issues) == 3
        
        # Verificar estructura de todos los issues
        for issue in issues:
            assert 'field' in issue
            assert 'label' in issue
            assert 'status' in issue
            assert 'days_left' in issue
            assert 'expires_on' in issue
            assert 'vehicle_id' in issue
            assert 'vehicle_plate' in issue
        
        # Verificar estados específicos
        statuses = [issue['status'] for issue in issues]
        assert 'expired' in statuses
        assert 'due_10' in statuses
        assert 'due_30' in statuses

    def test_issues_all_multiple_vehicles(
        self,
        vehicle_with_expired_cert,
        vehicle_with_due_10_matricula,
        vehicle_with_valid_dates
    ):
        """Test de issues_all con múltiples vehículos"""
        issues = VehicleIssuesCheck.issues_all()
        
        # Deben haber 2 issues
        assert len(issues) == 2
        
        # Verificar que los vehículos correctos están en los issues
        vehicle_ids = [issue['vehicle_id'] for issue in issues]
        assert vehicle_with_expired_cert.id in vehicle_ids
        assert vehicle_with_due_10_matricula.id in vehicle_ids
        assert vehicle_with_valid_dates.id not in vehicle_ids

    def test_issues_all_with_queryset(self, vehicle_with_expired_cert, vehicle_with_due_10_matricula):
        """Test de issues_all con queryset específico"""
        queryset = Vehicle.objects.filter(id=vehicle_with_expired_cert.id)
        issues = VehicleIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 1
        assert issues[0]['vehicle_id'] == vehicle_with_expired_cert.id

    def test_issues_all_empty_queryset(self):
        """Test de issues_all con queryset vacío"""
        queryset = Vehicle.objects.none()
        issues = VehicleIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 0

    def test_field_labels_complete(self):
        """Test que todos los campos tienen etiquetas definidas"""
        expected_fields = [
            'due_date_cert_oper',
            'due_date_matricula',
            'due_date_mtop',
            'due_date_technical_review',
            'insurance_expiration_date',
            'due_date_satellite'
        ]
        
        for field in expected_fields:
            assert field in VehicleIssuesCheck.FIELD_LABELS
            assert VehicleIssuesCheck.FIELD_LABELS[field]

    def test_warning_constants(self):
        """Test que las constantes de advertencia están correctamente definidas"""
        assert VehicleIssuesCheck.WARNING_30 == 30
        assert VehicleIssuesCheck.WARNING_10 == 10

    def test_issue_structure_complete(self, vehicle_with_expired_cert):
        """Test que la estructura de un issue contiene todos los campos necesarios"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_expired_cert)
        
        assert len(issues) > 0
        issue = issues[0]
        
        required_keys = [
            'field', 'label', 'status', 'days_left',
            'expires_on', 'vehicle_id', 'vehicle_plate'
        ]
        
        for key in required_keys:
            assert key in issue

    def test_expires_on_field(self, vehicle_with_expired_cert):
        """Test que el campo expires_on contiene la fecha correcta"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_expired_cert)
        
        assert issues[0]['expires_on'] == vehicle_with_expired_cert.due_date_cert_oper

    def test_vehicle_plate_field(self, vehicle_with_expired_cert):
        """Test que el campo vehicle_plate está presente y es correcto"""
        issues = VehicleIssuesCheck.issues_for(vehicle_with_expired_cert)
        
        assert issues[0]['vehicle_plate'] == vehicle_with_expired_cert.no_plate

    def test_boundary_condition_exactly_10_days(self):
        """Test de condición límite: exactamente 10 días"""
        exactly_10_days = date.today() + timedelta(days=10)
        status, days = VehicleIssuesCheck._evaluate(exactly_10_days)
        
        assert status == 'due_10'
        assert days == 10

    def test_boundary_condition_exactly_30_days(self):
        """Test de condición límite: exactamente 30 días"""
        exactly_30_days = date.today() + timedelta(days=30)
        status, days = VehicleIssuesCheck._evaluate(exactly_30_days)
        
        assert status == 'due_30'
        assert days == 30

    def test_boundary_condition_31_days(self):
        """Test de condición límite: 31 días (sin alerta)"""
        exactly_31_days = date.today() + timedelta(days=31)
        status, days = VehicleIssuesCheck._evaluate(exactly_31_days)
        
        assert status is None
        assert days is None

    def test_all_fields_checked(self):
        """Test que se verifican todos los campos del vehículo"""
        vehicle = Vehicle.objects.create(
            no_plate='TEST-001',
            brand='Test',
            model='Model',
            year=2020,
            due_date_cert_oper=date.today() - timedelta(days=1),
            due_date_matricula=date.today() + timedelta(days=5),
            due_date_mtop=date.today() + timedelta(days=15),
            due_date_technical_review=date.today() - timedelta(days=2),
            insurance_expiration_date=date.today() + timedelta(days=25),
            due_date_satellite=date.today() + timedelta(days=8)
        )
        
        issues = VehicleIssuesCheck.issues_for(vehicle)
        
        # Debe haber 6 issues
        assert len(issues) == 6
        
        # Verificar que todos los campos están presentes
        fields = [issue['field'] for issue in issues]
        assert 'due_date_cert_oper' in fields
        assert 'due_date_matricula' in fields
        assert 'due_date_mtop' in fields
        assert 'due_date_technical_review' in fields
        assert 'insurance_expiration_date' in fields
        assert 'due_date_satellite' in fields
