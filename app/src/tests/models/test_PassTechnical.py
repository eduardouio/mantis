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

    def test_bloque_free_text(self):
        technical = Technical.objects.create(
            first_name='Carlos',
            last_name='Rodríguez',
            dni='1122334455',
            nro_phone='0966555444'
        )
        
        # Test that bloque accepts any text (no longer restricted to choices)
        bloques = ['Petroecuador', 'Shaya', 'Mi Nuevo Bloque']
        for bloque in bloques:
            pass_tech = PassTechnical.objects.create(
                technical=technical,
                bloque=bloque,
                fecha_caducidad=date(2025, 12, 31)
            )
            assert pass_tech.bloque == bloque
            pass_tech.delete()

    def test_get_unique_bloques(self):
        technical = Technical.objects.create(
            first_name='Ana',
            last_name='López',
            dni='9988776655',
            nro_phone='0955444333'
        )
        PassTechnical.objects.create(
            technical=technical,
            bloque='Petroecuador',
            fecha_caducidad=date(2025, 12, 31)
        )
        PassTechnical.objects.create(
            technical=technical,
            bloque='Shaya',
            fecha_caducidad=date(2025, 6, 30)
        )
        bloques = PassTechnical.get_unique_bloques()
        assert 'Petroecuador' in bloques
        assert 'Shaya' in bloques
