# Archivo de pruebas para el modelo PassTechnical
# ...aquí van los tests para PassTechnical...
import pytest
from datetime import date
from accounts.models.PassTechnical import PassTechnical
from accounts.models.Technical import Technical


@pytest.mark.django_db
class TestPassTechnical:
    
    def test_create_pass_technical(self):
        technical = Technical.objects.create(
            first_name='Juan',
            last_name='Pérez',
            dni='1234567890',
            nro_phone='0987654321'
        )
        pass_technical = PassTechnical.objects.create(
            technical=technical,
            bloque='petroecuador',
            fecha_caducidad=date(2025, 12, 31)
        )
        assert pass_technical.technical == technical
        assert pass_technical.bloque == 'petroecuador'
        assert pass_technical.fecha_caducidad == date(2025, 12, 31)

    def test_get_by_technical_existing(self):
        technical = Technical.objects.create(
            first_name='María',
            last_name='González',
            dni='0987654321',
            nro_phone='0999888777'
        )
        pass_technical = PassTechnical.objects.create(
            technical=technical,
            bloque='shaya',
            fecha_caducidad=date(2025, 6, 30)
        )
        
        result = PassTechnical.get_by_technical(technical.id)
        assert result == pass_technical
        assert result.bloque == 'shaya'

    def test_get_by_technical_non_existing(self):
        result = PassTechnical.get_by_technical(999)  # Non-existing ID
        assert result is None

    def test_bloque_choices(self):
        technical = Technical.objects.create(
            first_name='Carlos',
            last_name='Rodríguez',
            dni='1122334455',
            nro_phone='0966555444'
        )
        
        # Test different bloque choices
        for bloque_code, _ in PassTechnical.BLOQUE_CHOICES:
            pass_tech = PassTechnical.objects.create(
                technical=technical,
                bloque=bloque_code,
                fecha_caducidad=date(2025, 12, 31)
            )
            assert pass_tech.bloque == bloque_code
            pass_tech.delete()  # Clean up for next iteration
