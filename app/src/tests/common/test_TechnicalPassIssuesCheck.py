import pytest
from datetime import date, timedelta
from common.TechnicalPassIssuesCheck import TechnicalPassIssuesCheck
from accounts.models import PassTechnical, Technical


@pytest.mark.django_db
class TestTechnicalPassIssuesCheck:

    @pytest.fixture
    def technical(self):
        """Técnico base para los tests"""
        return Technical.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@test.com'
        )

    @pytest.fixture
    def pass_expired(self, technical):
        """Pase vencido"""
        return PassTechnical.objects.create(
            technical=technical,
            bloque='petroecuador',
            fecha_caducidad=date.today() - timedelta(days=5)
        )

    @pytest.fixture
    def pass_due_10(self, technical):
        """Pase próximo a vencer en 10 días"""
        return PassTechnical.objects.create(
            technical=technical,
            bloque='shaya',
            fecha_caducidad=date.today() + timedelta(days=8)
        )

    @pytest.fixture
    def pass_due_30(self, technical):
        """Pase próximo a vencer en 30 días"""
        return PassTechnical.objects.create(
            technical=technical,
            bloque='consorcio_shushufindi',
            fecha_caducidad=date.today() + timedelta(days=25)
        )

    @pytest.fixture
    def pass_valid(self, technical):
        """Pase válido sin alertas"""
        return PassTechnical.objects.create(
            technical=technical,
            bloque='enap_sipec',
            fecha_caducidad=date.today() + timedelta(days=60)
        )

    @pytest.fixture
    def pass_no_date(self, technical):
        """Pase sin fecha de caducidad"""
        return PassTechnical.objects.create(
            technical=technical,
            bloque='orion',
            fecha_caducidad=None
        )

    @pytest.fixture
    def technical_with_multiple_passes(self):
        """Técnico con múltiples pases"""
        tech = Technical.objects.create(
            first_name='María',
            last_name='González',
            email='maria.gonzalez@test.com'
        )
        
        # Pase vencido
        PassTechnical.objects.create(
            technical=tech,
            bloque='petroecuador',
            fecha_caducidad=date.today() - timedelta(days=10)
        )
        
        # Pase próximo a vencer (10 días)
        PassTechnical.objects.create(
            technical=tech,
            bloque='shaya',
            fecha_caducidad=date.today() + timedelta(days=5)
        )
        
        # Pase válido
        PassTechnical.objects.create(
            technical=tech,
            bloque='consorcio_shushufindi',
            fecha_caducidad=date.today() + timedelta(days=90)
        )
        
        return tech

    def test_evaluate_expired_date(self):
        """Test que _evaluate detecta fechas vencidas"""
        expired_date = date.today() - timedelta(days=5)
        status, days = TechnicalPassIssuesCheck._evaluate(expired_date)
        
        assert status == 'expired'
        assert days == -5

    def test_evaluate_due_10_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (10 días)"""
        due_date = date.today() + timedelta(days=8)
        status, days = TechnicalPassIssuesCheck._evaluate(due_date)
        
        assert status == 'due_10'
        assert days == 8

    def test_evaluate_due_30_days(self):
        """Test que _evaluate detecta fechas próximas a vencer (30 días)"""
        due_date = date.today() + timedelta(days=25)
        status, days = TechnicalPassIssuesCheck._evaluate(due_date)
        
        assert status == 'due_30'
        assert days == 25

    def test_evaluate_valid_date(self):
        """Test que _evaluate retorna None para fechas válidas"""
        valid_date = date.today() + timedelta(days=60)
        status, days = TechnicalPassIssuesCheck._evaluate(valid_date)
        
        assert status is None
        assert days is None

    def test_evaluate_none_date(self):
        """Test que _evaluate maneja correctamente fechas None"""
        status, days = TechnicalPassIssuesCheck._evaluate(None)
        
        assert status is None
        assert days is None

    def test_issues_for_expired_pass(self, pass_expired):
        """Test de issues_for con pase vencido"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_expired)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'fecha_caducidad'
        assert issues[0]['label'] == f"Pase {pass_expired.get_bloque_display()}"
        assert issues[0]['status'] == 'expired'
        assert issues[0]['days_left'] == -5
        assert issues[0]['pass_id'] == pass_expired.id
        assert issues[0]['technical_id'] == pass_expired.technical_id
        assert issues[0]['technical_name'] == 'Juan Pérez'
        assert issues[0]['bloque'] == 'petroecuador'

    def test_issues_for_due_10_pass(self, pass_due_10):
        """Test de issues_for con pase próximo a vencer (10 días)"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_due_10)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'fecha_caducidad'
        assert issues[0]['status'] == 'due_10'
        assert issues[0]['days_left'] == 8
        assert issues[0]['bloque'] == 'shaya'

    def test_issues_for_due_30_pass(self, pass_due_30):
        """Test de issues_for con pase próximo a vencer (30 días)"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_due_30)
        
        assert len(issues) == 1
        assert issues[0]['field'] == 'fecha_caducidad'
        assert issues[0]['status'] == 'due_30'
        assert issues[0]['days_left'] == 25
        assert issues[0]['bloque'] == 'consorcio_shushufindi'

    def test_issues_for_valid_pass(self, pass_valid):
        """Test de issues_for con pase válido sin alertas"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_valid)
        
        assert len(issues) == 0

    def test_issues_for_pass_no_date(self, pass_no_date):
        """Test de issues_for con pase sin fecha de caducidad"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_no_date)
        
        assert len(issues) == 0

    def test_issues_all_multiple_passes(
        self,
        pass_expired,
        pass_due_10,
        pass_valid
    ):
        """Test de issues_all con múltiples pases"""
        issues = TechnicalPassIssuesCheck.issues_all()
        
        # Filtrar solo los issues de los pases creados en este test
        test_pass_ids = [pass_expired.id, pass_due_10.id, pass_valid.id]
        test_issues = [issue for issue in issues if issue['pass_id'] in test_pass_ids]
        
        # Deben haber 2 issues (pase vencido y pase próximo a vencer)
        assert len(test_issues) == 2
        
        # Verificar que los pases correctos están en los issues
        pass_ids = [issue['pass_id'] for issue in test_issues]
        assert pass_expired.id in pass_ids
        assert pass_due_10.id in pass_ids
        assert pass_valid.id not in pass_ids

    def test_issues_all_with_queryset(self, pass_expired, pass_due_10):
        """Test de issues_all con queryset específico"""
        queryset = PassTechnical.objects.filter(id=pass_expired.id)
        issues = TechnicalPassIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 1
        assert issues[0]['pass_id'] == pass_expired.id

    def test_issues_all_empty_queryset(self):
        """Test de issues_all con queryset vacío"""
        queryset = PassTechnical.objects.none()
        issues = TechnicalPassIssuesCheck.issues_all(queryset=queryset)
        
        assert len(issues) == 0

    def test_technical_with_multiple_passes(self, technical_with_multiple_passes):
        """Test de técnico con múltiples pases"""
        passes = PassTechnical.objects.filter(technical=technical_with_multiple_passes)
        all_issues = []
        
        for pass_record in passes:
            all_issues.extend(TechnicalPassIssuesCheck.issues_for(pass_record))
        
        # Deben haber 2 issues (vencido y próximo a vencer en 10 días)
        assert len(all_issues) == 2
        
        statuses = [issue['status'] for issue in all_issues]
        assert 'expired' in statuses
        assert 'due_10' in statuses

    def test_warning_constants(self):
        """Test que las constantes de advertencia están correctamente definidas"""
        assert TechnicalPassIssuesCheck.WARNING_30 == 30
        assert TechnicalPassIssuesCheck.WARNING_10 == 10

    def test_issue_structure_complete(self, pass_expired):
        """Test que la estructura de un issue contiene todos los campos necesarios"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_expired)
        
        assert len(issues) > 0
        issue = issues[0]
        
        required_keys = [
            'field', 'label', 'status', 'days_left',
            'expires_on', 'pass_id', 'technical_id',
            'technical_name', 'bloque'
        ]
        
        for key in required_keys:
            assert key in issue

    def test_technical_name_format(self, pass_expired):
        """Test que el nombre del técnico se formatea correctamente"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_expired)
        
        assert issues[0]['technical_name'] == 'Juan Pérez'
        assert issues[0]['technical_name'] == f"{pass_expired.technical.first_name} {pass_expired.technical.last_name}"

    def test_expires_on_field(self, pass_expired):
        """Test que el campo expires_on contiene la fecha correcta"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_expired)
        
        assert issues[0]['expires_on'] == pass_expired.fecha_caducidad

    def test_bloque_field(self, pass_expired):
        """Test que el campo bloque está presente y es correcto"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_expired)
        
        assert issues[0]['bloque'] == pass_expired.bloque

    def test_pass_id_field(self, pass_expired):
        """Test que el campo pass_id está presente y es correcto"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_expired)
        
        assert issues[0]['pass_id'] == pass_expired.id

    def test_label_uses_display_value(self, pass_expired):
        """Test que el label usa get_bloque_display()"""
        issues = TechnicalPassIssuesCheck.issues_for(pass_expired)
        expected_label = f"Pase {pass_expired.get_bloque_display()}"
        
        assert issues[0]['label'] == expected_label

    def test_boundary_condition_exactly_10_days(self):
        """Test de condición límite: exactamente 10 días"""
        exactly_10_days = date.today() + timedelta(days=10)
        status, days = TechnicalPassIssuesCheck._evaluate(exactly_10_days)
        
        assert status == 'due_10'
        assert days == 10

    def test_boundary_condition_exactly_30_days(self):
        """Test de condición límite: exactamente 30 días"""
        exactly_30_days = date.today() + timedelta(days=30)
        status, days = TechnicalPassIssuesCheck._evaluate(exactly_30_days)
        
        assert status == 'due_30'
        assert days == 30

    def test_boundary_condition_31_days(self):
        """Test de condición límite: 31 días (sin alerta)"""
        exactly_31_days = date.today() + timedelta(days=31)
        status, days = TechnicalPassIssuesCheck._evaluate(exactly_31_days)
        
        assert status is None
        assert days is None

    def test_boundary_condition_exactly_0_days(self):
        """Test de condición límite: exactamente hoy (día 0)"""
        today = date.today()
        status, days = TechnicalPassIssuesCheck._evaluate(today)
        
        assert status == 'due_10'
        assert days == 0

    def test_issues_all_sorting(self, technical):
        """Test que los issues se pueden ordenar por días restantes"""
        # Crear pases con diferentes fechas
        pass1 = PassTechnical.objects.create(
            technical=technical,
            bloque='petroecuador',
            fecha_caducidad=date.today() - timedelta(days=5)
        )
        pass2 = PassTechnical.objects.create(
            technical=technical,
            bloque='shaya',
            fecha_caducidad=date.today() + timedelta(days=2)
        )
        pass3 = PassTechnical.objects.create(
            technical=technical,
            bloque='consorcio_shushufindi',
            fecha_caducidad=date.today() + timedelta(days=20)
        )
        
        issues = TechnicalPassIssuesCheck.issues_all()
        
        # Filtrar solo los issues de este test
        test_pass_ids = [pass1.id, pass2.id, pass3.id]
        test_issues = [issue for issue in issues if issue['pass_id'] in test_pass_ids]
        
        # Verificar que hay 3 issues
        assert len(test_issues) == 3
        
        # Ordenar por días restantes
        sorted_issues = sorted(test_issues, key=lambda x: x['days_left'])
        
        # El primero debe ser el vencido (días negativos)
        assert sorted_issues[0]['days_left'] < 0
        assert sorted_issues[0]['status'] == 'expired'

    def test_multiple_technicals_with_passes(self):
        """Test con múltiples técnicos cada uno con sus pases"""
        tech1 = Technical.objects.create(
            first_name='Carlos',
            last_name='López',
            email='carlos@test.com'
        )
        tech2 = Technical.objects.create(
            first_name='Ana',
            last_name='Martínez',
            email='ana@test.com'
        )
        
        # Pases para técnico 1
        pass1 = PassTechnical.objects.create(
            technical=tech1,
            bloque='petroecuador',
            fecha_caducidad=date.today() - timedelta(days=5)
        )
        
        # Pases para técnico 2
        pass2 = PassTechnical.objects.create(
            technical=tech2,
            bloque='shaya',
            fecha_caducidad=date.today() + timedelta(days=8)
        )
        
        issues = TechnicalPassIssuesCheck.issues_all()
        
        # Filtrar solo los issues de este test
        test_pass_ids = [pass1.id, pass2.id]
        test_issues = [issue for issue in issues if issue['pass_id'] in test_pass_ids]
        
        # Deben haber 2 issues, uno por cada técnico
        assert len(test_issues) == 2
        
        technical_ids = [issue['technical_id'] for issue in test_issues]
        assert tech1.id in technical_ids
        assert tech2.id in technical_ids
