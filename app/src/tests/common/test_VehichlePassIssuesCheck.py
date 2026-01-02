import pytest
from datetime import date, timedelta
from common.VehichlePassIssuesCheck import PassVehichleIssuesCheck
from equipment.models import PassVehicle, Vehicle


@pytest.mark.django_db
class TestPassVehichleIssuesCheck:

    @pytest.fixture
    def vehicle(self):
        """Vehículo base para los tests"""
        return Vehicle.objects.create(
            no_plate='ABC-1234',
            brand='Toyota',
            model='Hilux',
            type_vehicle='CAMIONETA',
            year=2020
        )

    @pytest.fixture
    def pass_expired(self, vehicle):
        """Pase vencido"""
        return PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() - timedelta(days=5)
        )

    @pytest.fixture
    def pass_due_10(self, vehicle):
        """Pase próximo a vencer en 10 días"""
        return PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='SHAYA',
            fecha_caducidad=date.today() + timedelta(days=8)
        )

    @pytest.fixture
    def pass_due_30(self, vehicle):
        """Pase próximo a vencer en 30 días"""
        return PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='CONSORCIO SHUSHUFINDI',
            fecha_caducidad=date.today() + timedelta(days=25)
        )

    @pytest.fixture
    def pass_valid(self, vehicle):
        """Pase válido sin alertas"""
        return PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='ENAP SIPEC',
            fecha_caducidad=date.today() + timedelta(days=60)
        )

    @pytest.fixture
    def pass_no_date(self, vehicle):
        """Pase sin fecha de caducidad"""
        return PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='ORION',
            fecha_caducidad=None
        )

    def test_evaluate_expired_date(self):
        """Test que _evaluate detecta fechas vencidas"""
        expired_date = date.today() - timedelta(days=5)
        status, days = PassVehichleIssuesCheck._evaluate(expired_date)
        
        assert status == 'expired'
        assert days == -5

    def test_evaluate_due_10_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (10 días)"""
        due_date = date.today() + timedelta(days=8)
        status, days = PassVehichleIssuesCheck._evaluate(due_date)
        
        assert status == 'due_10'
        assert days == 8

    def test_evaluate_due_30_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (30 días)"""
        due_date = date.today() + timedelta(days=25)
        status, days = PassVehichleIssuesCheck._evaluate(due_date)
        
        assert status == 'due_30'
        assert days == 25

    def test_evaluate_valid_date(self):
        """Test que _evaluate retorna None para fechas válidas"""
        valid_date = date.today() + timedelta(days=60)
        status, days = PassVehichleIssuesCheck._evaluate(valid_date)
        
        assert status is None
        assert days is None

    def test_evaluate_none_date(self):
        """Test que _evaluate maneja correctamente fechas None"""
        status, days = PassVehichleIssuesCheck._evaluate(None)
        
        assert status is None
        assert days is None

    def test_issues_for_expired_pass(self, pass_expired):
        """Test de issues_for con pase vencido"""
        issues = PassVehichleIssuesCheck.issues_for(pass_expired)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'fecha_caducidad'
        assert issues[0]['label'] == f"Pase {pass_expired.get_bloque_display()}"
        assert issues[0]['status'] == 'expired'
        assert issues[0]['days_left'] == -5
        assert issues[0]['pass_id'] == pass_expired.id
        assert issues[0]['vehicle_id'] == pass_expired.vehicle_id
        assert issues[0]['vehicle_plate'] == 'ABC-1234'
        assert issues[0]['bloque'] == 'PETROECUADOR'

    def test_issues_for_due_10_pass(self, pass_due_10):
        """Test de issues_for con pase próximo a vencer (10 días)"""
        issues = PassVehichleIssuesCheck.issues_for(pass_due_10)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'fecha_caducidad'
        assert issues[0]['status'] == 'due_10'
        assert issues[0]['days_left'] == 8
        assert issues[0]['bloque'] == 'SHAYA'

    def test_issues_for_due_30_pass(self, pass_due_30):
        """Test de issues_for con pase próximo a vencer (30 días)"""
        issues = PassVehichleIssuesCheck.issues_for(pass_due_30)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'fecha_caducidad'
        assert issues[0]['status'] == 'due_30'
        assert issues[0]['days_left'] == 25
        assert issues[0]['bloque'] == 'CONSORCIO SHUSHUFINDI'

    def test_issues_for_valid_pass(self, pass_valid):
        """Test de issues_for con pase válido sin alertas"""
        issues = PassVehichleIssuesCheck.issues_for(pass_valid)
        
        assert len(issues) == 0

    def test_issues_for_pass_no_date(self, pass_no_date):
        """Test de issues_for con pase sin fecha de caducidad"""
        issues = PassVehichleIssuesCheck.issues_for(pass_no_date)
        
        assert len(issues) == 0

    def test_issues_all_multiple_passes(self, pass_expired, pass_due_10, pass_valid):
        """Test de issues_all con múltiples pases"""
        issues = PassVehichleIssuesCheck.issues_all()
        
        # Filtrar solo los issues de los pases creados en este test
        test_pass_ids = [pass_expired.id, pass_due_10.id, pass_valid.id]
        test_issues = [issue for issue in issues if issue['pass_id'] in test_pass_ids]
        
        # Deben haber 2 issues
        assert len(test_issues) == 2
        
        # Verificar que los pases correctos están en los issues
        pass_ids = [issue['pass_id'] for issue in test_issues]
        assert pass_expired.id in pass_ids
        assert pass_due_10.id in pass_ids
        assert pass_valid.id not in pass_ids

    def test_issues_all_with_queryset(self, pass_expired, pass_due_10):
        """Test de issues_all con queryset específico"""
        queryset = PassVehicle.objects.filter(id=pass_expired.id)
        issues = PassVehichleIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 1
        assert issues[0]['pass_id'] == pass_expired.id

    def test_issues_all_empty_queryset(self):
        """Test de issues_all con queryset vacío"""
        queryset = PassVehicle.objects.none()
        issues = PassVehichleIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 0

    def test_warning_constants(self):
        """Test que las constantes de advertencia están correctamente definidas"""
        assert PassVehichleIssuesCheck.WARNING_30 == 30
        assert PassVehichleIssuesCheck.WARNING_10 == 10

    def test_issue_structure_complete(self, pass_expired):
        """Test que la estructura de un issue contiene todos los campos necesarios"""
        issues = PassVehichleIssuesCheck.issues_for(pass_expired)
        
        assert len(issues) > 0
        issue = issues[0]
        
        required_keys = [
            'field', 'label', 'status', 'days_left',
            'expires_on', 'pass_id', 'vehicle_id',
            'vehicle_plate', 'bloque'
        ]
        
        for key in required_keys:
            assert key in issue

    def test_vehicle_plate_field(self, pass_expired):
        """Test que el campo vehicle_plate contiene la placa correcta"""
        issues = PassVehichleIssuesCheck.issues_for(pass_expired)
        
        assert issues[0]['vehicle_plate'] == pass_expired.vehicle.no_plate

    def test_expires_on_field(self, pass_expired):
        """Test que el campo expires_on contiene la fecha correcta"""
        issues = PassVehichleIssuesCheck.issues_for(pass_expired)
        
        assert issues[0]['expires_on'] == pass_expired.fecha_caducidad

    def test_label_uses_display_value(self, pass_expired):
        """Test que el label usa get_bloque_display()"""
        issues = PassVehichleIssuesCheck.issues_for(pass_expired)
        expected_label = f"Pase {pass_expired.get_bloque_display()}"
        
        assert issues[0]['label'] == expected_label

    def test_boundary_condition_exactly_10_days(self):
        """Test de condición límite: exactamente 10 días"""
        exactly_10_days = date.today() + timedelta(days=10)
        status, days = PassVehichleIssuesCheck._evaluate(exactly_10_days)
        
        assert status == 'due_10'
        assert days == 10

    def test_boundary_condition_exactly_30_days(self):
        """Test de condición límite: exactamente 30 días"""
        exactly_30_days = date.today() + timedelta(days=30)
        status, days = PassVehichleIssuesCheck._evaluate(exactly_30_days)
        
        assert status == 'due_30'
        assert days == 30

    def test_boundary_condition_31_days(self):
        """Test de condición límite: 31 días (sin alerta)"""
        exactly_31_days = date.today() + timedelta(days=31)
        status, days = PassVehichleIssuesCheck._evaluate(exactly_31_days)
        
        assert status is None
        assert days is None

    def test_multiple_vehicles_with_passes(self):
        """Test con múltiples vehículos cada uno con sus pases"""
        vehicle1 = Vehicle.objects.create(
            no_plate='VEH-001',
            brand='Toyota',
            model='Hilux',
            type_vehicle='CAMIONETA',
            year=2020
        )
        vehicle2 = Vehicle.objects.create(
            no_plate='VEH-002',
            brand='Chevrolet',
            model='D-Max',
            type_vehicle='CAMIONETA',
            year=2021
        )
        
        pass1 = PassVehicle.objects.create(
            vehicle=vehicle1,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() - timedelta(days=5)
        )
        
        pass2 = PassVehicle.objects.create(
            vehicle=vehicle2,
            bloque='SHAYA',
            fecha_caducidad=date.today() + timedelta(days=8)
        )
        
        issues = PassVehichleIssuesCheck.issues_all()
        
        # Filtrar solo los issues de este test
        test_pass_ids = [pass1.id, pass2.id]
        test_issues = [issue for issue in issues if issue['pass_id'] in test_pass_ids]
        
        # Deben haber 2 issues, uno por cada vehículo
        assert len(test_issues) == 2
        
        vehicle_ids = [issue['vehicle_id'] for issue in test_issues]
        assert vehicle1.id in vehicle_ids
        assert vehicle2.id in vehicle_ids
