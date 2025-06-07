# Archivo de pruebas para el modelo Partner
# ...aquí van los tests para Partner...

import pytest
from projects.models.Partner import Partner


@pytest.mark.django_db
class TestPartner:
    
    def test_create_partner(self):
        partner = Partner.objects.create(
            business_tax_id='1234567890001',
            name='PEISOL S.A.',
            email='contacto@peisol.com',
            phone='0987654321',
            address='Av. Principal 123',
            name_contact='Juan Pérez'
        )
        assert partner.business_tax_id == '1234567890001'
        assert partner.name == 'PEISOL S.A.'
        assert partner.email == 'contacto@peisol.com'
        assert partner.phone == '0987654321'
        assert partner.address == 'Av. Principal 123'
        assert partner.name_contact == 'Juan Pérez'

    def test_partner_str(self):
        partner = Partner.objects.create(
            business_tax_id='0987654321001',
            name='Empresa ABC',
            address='Calle Secundaria 456'
        )
        assert str(partner) == 'Empresa ABC'

    def test_partner_unique_business_tax_id(self):
        Partner.objects.create(
            business_tax_id='1111111111001',
            name='Primera Empresa',
            address='Dirección 1'
        )
        
        # Should raise IntegrityError for duplicate business_tax_id
        with pytest.raises(Exception):
            Partner.objects.create(
                business_tax_id='1111111111001',
                name='Segunda Empresa',
                address='Dirección 2'
            )

    def test_partner_optional_fields(self):
        partner = Partner.objects.create(
            business_tax_id='2222222222001',
            name='Empresa Mínima',
            address='Dirección Básica'
            # email, phone, name_contact are optional
        )
        assert partner.email is None or partner.email == ''
        assert partner.phone is None or partner.phone == ''
        assert partner.name_contact is None or partner.name_contact == ''
        assert partner.name == 'Empresa Mínima'

    def test_partner_with_all_fields(self):
        partner = Partner.objects.create(
            business_tax_id='3333333333001',
            name='Empresa Completa',
            email='info@empresa.com',
            phone='0999888777',
            address='Av. Completa 789',
            name_contact='María González'
        )
        assert all([
            partner.business_tax_id,
            partner.name,
            partner.email,
            partner.phone,
            partner.address,
            partner.name_contact
        ])
