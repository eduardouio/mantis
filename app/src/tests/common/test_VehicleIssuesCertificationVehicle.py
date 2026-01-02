import pytest
from datetime import date, timedelta
from common.VehicleIssuesCertificationVehicle import VehicleIssuesCertificationVehicle
from equipment.models import CertificationVehicle, Vehicle


@pytest.mark.django_db
class TestVehicleIssuesCertificationVehicle:

    @pytest.fixture
    def vehicle(self):
        """Vehículo base para los tests"""
        return Vehicle.objects.create(
            no_plate='ABC-1234',
            brand='Toyota',
            model='Hilux',
            year=2020
        )

    @pytest.fixture
    def cert_expired(self, vehicle):
        """Certificación vencida"""
        return CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='GPS',
            date_start=date.today() - timedelta(days=365),
            date_end=date.today() - timedelta(days=5),
            is_active=True
        )

    @pytest.fixture
    def cert_due_10(self, vehicle):
        """Certificación próxima a vencer en 10 días"""
        return CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='EXTINTOR',
            date_start=date.today() - timedelta(days=350),
            date_end=date.today() + timedelta(days=8),
            is_active=True
        )

    @pytest.fixture
    def cert_due_30(self, vehicle):
        """Certificación próxima a vencer en 30 días"""
        return CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='BOTIQUIN',
            date_start=date.today() - timedelta(days=300),
            date_end=date.today() + timedelta(days=25),
            is_active=True
        )

    @pytest.fixture
    def cert_valid(self, vehicle):
        """Certificación válida sin alertas"""
        return CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='TRIANGULOS',
            date_start=date.today() - timedelta(days=30),
            date_end=date.today() + timedelta(days=60),
            is_active=True
        )

    @pytest.fixture
    def cert_no_end_date(self, vehicle):
        """Certificación sin fecha de fin"""
        return CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='GPS',
            date_start=date.today(),
            date_end=None,
            is_active=True
        )

    @pytest.fixture
    def cert_inactive(self, vehicle):
        """Certificación inactiva"""
        return CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='GPS',
            date_start=date.today() - timedelta(days=365),
            date_end=date.today() + timedelta(days=5),
            is_active=False
        )

    @pytest.fixture
    def vehicle_with_multiple_certs(self):
        """Vehículo con múltiples certificaciones"""
        vehicle = Vehicle.objects.create(
            no_plate='XYZ-5678',
            brand='Chevrolet',
            model='D-Max',
            year=2021
        )
        
        # Certificación vencida
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='GPS',
            date_start=date.today() - timedelta(days=365),
            date_end=date.today() - timedelta(days=10),
            is_active=True
        )
        
        # Certificación próxima a vencer (10 días)
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='EXTINTOR',
            date_start=date.today() - timedelta(days=350),
            date_end=date.today() + timedelta(days=5),
            is_active=True
        )
        
        # Certificación próxima a vencer (30 días)
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='BOTIQUIN',
            date_start=date.today() - timedelta(days=300),
            date_end=date.today() + timedelta(days=20),
            is_active=True
        )
        
        # Certificación válida
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='TRIANGULOS',
            date_start=date.today() - timedelta(days=30),
            date_end=date.today() + timedelta(days=90),
            is_active=True
        )
        
        return vehicle

    def test_evaluate_expired_date(self):
        """Test que _evaluate detecta fechas vencidas"""
        expired_date = date.today() - timedelta(days=5)
        status, days = VehicleIssuesCertificationVehicle._evaluate(expired_date)
        
        assert status == 'expired'
        assert days == -5

    def test_evaluate_due_10_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (10 días)"""
        due_date = date.today() + timedelta(days=8)
        status, days = VehicleIssuesCertificationVehicle._evaluate(due_date)
        
        assert status == 'due_10'
        assert days == 8

    def test_evaluate_due_30_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (30 días)"""
        due_date = date.today() + timedelta(days=25)
        status, days = VehicleIssuesCertificationVehicle._evaluate(due_date)
        
        assert status == 'due_30'
        assert days == 25

    def test_evaluate_valid_date(self):
        """Test que _evaluate retorna None para fechas válidas"""
        valid_date = date.today() + timedelta(days=60)
        status, days = VehicleIssuesCertificationVehicle._evaluate(valid_date)
        
        assert status is None
        assert days is None

    def test_evaluate_none_date(self):
        """Test que _evaluate maneja correctamente fechas None"""
        status, days = VehicleIssuesCertificationVehicle._evaluate(None)
        
        assert status is None
        assert days is None

    def test_issues_for_expired_cert(self, vehicle, cert_expired):
        """Test de issues_for con certificación vencida"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'date_end'
        assert 'Certificación' in issues[0]['label']
        assert issues[0]['status'] == 'expired'
        assert issues[0]['days_left'] == -5
        assert issues[0]['certification_id'] == cert_expired.id
        assert issues[0]['vehicle_id'] == vehicle.id
        assert issues[0]['vehicle_plate'] == 'ABC-1234'
        assert issues[0]['certification_type'] == 'GPS'

    def test_issues_for_due_10_cert(self, vehicle, cert_due_10):
        """Test de issues_for con certificación próxima a vencer (10 días)"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'date_end'
        assert issues[0]['status'] == 'due_10'
        assert issues[0]['days_left'] == 8
        assert issues[0]['certification_type'] == 'EXTINTOR'

    def test_issues_for_due_30_cert(self, vehicle, cert_due_30):
        """Test de issues_for con certificación próxima a vencer (30 días)"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'date_end'
        assert issues[0]['status'] == 'due_30'
        assert issues[0]['days_left'] == 25
        assert issues[0]['certification_type'] == 'BOTIQUIN'

    def test_issues_for_valid_cert(self, vehicle, cert_valid):
        """Test de issues_for con certificación válida sin alertas"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) == 0

    def test_issues_for_cert_no_end_date(self, vehicle, cert_no_end_date):
        """Test de issues_for con certificación sin fecha de fin"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) == 0

    def test_issues_for_cert_inactive(self, vehicle, cert_inactive):
        """Test de issues_for no incluye certificaciones inactivas"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) == 0

    def test_issues_for_vehicle_with_multiple_certs(self, vehicle_with_multiple_certs):
        """Test de issues_for con vehículo con múltiples certificaciones"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle_with_multiple_certs)
        
        # Deben haber 3 issues (vencida, due_10, due_30)
        assert len(issues) == 3
        
        # Verificar estados
        statuses = [issue['status'] for issue in issues]
        assert 'expired' in statuses
        assert 'due_10' in statuses
        assert 'due_30' in statuses

    def test_issues_all_multiple_vehicles(self, vehicle, cert_expired, cert_due_10):
        """Test de issues_all con múltiples vehículos"""
        # Crear otro vehículo con certificación
        vehicle2 = Vehicle.objects.create(
            no_plate='DEF-9012',
            brand='Ford',
            model='Ranger',
            year=2019
        )
        CertificationVehicle.objects.create(
            vehicle=vehicle2,
            name='GPS',
            date_start=date.today() - timedelta(days=350),
            date_end=date.today() + timedelta(days=5),
            is_active=True
        )
        
        issues = VehicleIssuesCertificationVehicle.issues_all()
        
        # Deben haber 3 issues totales
        assert len(issues) == 3
        
        # Verificar que ambos vehículos están representados
        vehicle_ids = [issue['vehicle_id'] for issue in issues]
        assert vehicle.id in vehicle_ids
        assert vehicle2.id in vehicle_ids

    def test_issues_all_with_queryset(self, vehicle, cert_expired):
        """Test de issues_all con queryset específico"""
        # Crear otro vehículo que no debe incluirse
        vehicle2 = Vehicle.objects.create(
            no_plate='GHI-3456',
            brand='Nissan',
            model='Frontier',
            year=2022
        )
        CertificationVehicle.objects.create(
            vehicle=vehicle2,
            name='GPS',
            date_start=date.today() - timedelta(days=365),
            date_end=date.today() - timedelta(days=3),
            is_active=True
        )
        
        # Filtrar solo el primer vehículo
        queryset = Vehicle.objects.filter(id=vehicle.id)
        issues = VehicleIssuesCertificationVehicle.issues_all(queryset=queryset)
        
        assert len(issues) == 1
        assert issues[0]['vehicle_id'] == vehicle.id

    def test_issues_all_empty_queryset(self):
        """Test de issues_all con queryset vacío"""
        queryset = Vehicle.objects.none()
        issues = VehicleIssuesCertificationVehicle.issues_all(queryset=queryset)
        
        assert len(issues) == 0

    def test_warning_constants(self):
        """Test que las constantes de advertencia están correctamente definidas"""
        assert VehicleIssuesCertificationVehicle.WARNING_30 == 30
        assert VehicleIssuesCertificationVehicle.WARNING_10 == 10

    def test_issue_structure_complete(self, vehicle, cert_expired):
        """Test que la estructura de un issue contiene todos los campos necesarios"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) > 0
        issue = issues[0]
        
        required_keys = [
            'field', 'label', 'status', 'days_left',
            'expires_on', 'certification_id', 'vehicle_id',
            'vehicle_plate', 'certification_type'
        ]
        
        for key in required_keys:
            assert key in issue

    def test_vehicle_plate_field(self, vehicle, cert_expired):
        """Test que el campo vehicle_plate contiene la placa correcta"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert issues[0]['vehicle_plate'] == vehicle.no_plate

    def test_expires_on_field(self, vehicle, cert_expired):
        """Test que el campo expires_on contiene la fecha correcta"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert issues[0]['expires_on'] == cert_expired.date_end

    def test_certification_type_field(self, vehicle, cert_expired):
        """Test que el campo certification_type está presente y es correcto"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert issues[0]['certification_type'] == cert_expired.name

    def test_label_format(self, vehicle, cert_expired):
        """Test que el label incluye el nombre de la certificación"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        label = issues[0]['label']
        assert 'Certificación' in label
        assert cert_expired.get_name_display() in label

    def test_boundary_condition_exactly_10_days(self):
        """Test de condición límite: exactamente 10 días"""
        exactly_10_days = date.today() + timedelta(days=10)
        status, days = VehicleIssuesCertificationVehicle._evaluate(exactly_10_days)
        
        assert status == 'due_10'
        assert days == 10

    def test_boundary_condition_exactly_30_days(self):
        """Test de condición límite: exactamente 30 días"""
        exactly_30_days = date.today() + timedelta(days=30)
        status, days = VehicleIssuesCertificationVehicle._evaluate(exactly_30_days)
        
        assert status == 'due_30'
        assert days == 30

    def test_boundary_condition_31_days(self):
        """Test de condición límite: 31 días (sin alerta)"""
        exactly_31_days = date.today() + timedelta(days=31)
        status, days = VehicleIssuesCertificationVehicle._evaluate(exactly_31_days)
        
        assert status is None
        assert days is None

    def test_only_active_certifications(self, vehicle):
        """Test que solo se consideran certificaciones activas"""
        # Certificación activa vencida
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='GPS',
            date_start=date.today() - timedelta(days=365),
            date_end=date.today() - timedelta(days=5),
            is_active=True
        )
        
        # Certificación inactiva vencida (no debe aparecer)
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='EXTINTOR',
            date_start=date.today() - timedelta(days=365),
            date_end=date.today() - timedelta(days=10),
            is_active=False
        )
        
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        # Solo debe haber 1 issue (la activa)
        assert len(issues) == 1
        assert issues[0]['certification_type'] == 'GPS'

    def test_vehicle_without_certifications(self, vehicle):
        """Test con vehículo sin certificaciones"""
        issues = VehicleIssuesCertificationVehicle.issues_for(vehicle)
        
        assert len(issues) == 0

    def test_issues_all_no_vehicles(self):
        """Test de issues_all sin vehículos en la base de datos"""
        issues = VehicleIssuesCertificationVehicle.issues_all()
        
        assert len(issues) == 0
