import json
from datetime import date, timedelta

import pytest
from django.test import Client

from accounts.models import CustomUserModel
from projects.models import Partner, Project
from projects.models.ShippingGuide import ShippingGuide


@pytest.mark.django_db
class TestShippingGuidePlaces:
    @pytest.fixture
    def client_logged(self):
        user, _ = CustomUserModel.objects.get_or_create(
            email='shipping-guide@test.com',
            defaults={
                'first_name': 'Shipping',
                'last_name': 'Tester',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        client = Client(raise_request_exception=False)
        client.force_login(user)
        return client

    @pytest.fixture
    def test_user(self):
        user, _ = CustomUserModel.objects.get_or_create(
            email='shipping-guide@test.com',
            defaults={
                'first_name': 'Shipping',
                'last_name': 'Tester',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        return user

    @pytest.fixture
    def test_partner(self, test_user):
        return Partner.objects.create(
            name='PEISOL CLIENTE',
            business_tax_id='1799999999001',
            email='cliente@test.com',
            phone='0999999999',
            address='Quito, Ecuador',
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_project(self, test_partner, test_user):
        return Project.objects.create(
            partner=test_partner,
            location='MDC 40 / Sacha',
            contact_name='Ing. Catalina Velandia',
            contact_phone='+593984066240',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    def _build_payload(self, test_project, guide_type):
        return {
            'project_id': test_project.id,
            'type_shipping_guide': guide_type,
            'issue_date': date.today().isoformat(),
            'origin_place': 'ORIGEN MANUAL',
            'destination_place': 'DESTINO MANUAL',
            'carrier_name': 'Transportista Demo',
            'details': [],
        }

    def test_create_exit_guide_preserves_manual_places(self, client_logged, test_project):
        response = client_logged.post(
            '/api/shipping/guides/',
            data=json.dumps(self._build_payload(test_project, 'EXIT')),
            content_type='application/json',
        )

        assert response.status_code == 201
        payload = response.json()['data']
        guide = ShippingGuide.objects.get(pk=payload['id'])

        assert payload['origin_place'] == 'ORIGEN MANUAL'
        assert payload['destination_place'] == 'DESTINO MANUAL'
        assert guide.origin_place == 'ORIGEN MANUAL'
        assert guide.destination_place == 'DESTINO MANUAL'

    def test_create_in_guide_preserves_manual_places(self, client_logged, test_project):
        response = client_logged.post(
            '/api/shipping/guides/',
            data=json.dumps(self._build_payload(test_project, 'IN')),
            content_type='application/json',
        )

        assert response.status_code == 201
        payload = response.json()['data']
        guide = ShippingGuide.objects.get(pk=payload['id'])

        assert payload['origin_place'] == 'ORIGEN MANUAL'
        assert payload['destination_place'] == 'DESTINO MANUAL'
        assert guide.origin_place == 'ORIGEN MANUAL'
        assert guide.destination_place == 'DESTINO MANUAL'

    def test_create_transfer_guide_preserves_manual_places(self, client_logged, test_project):
        response = client_logged.post(
            '/api/shipping/guides/',
            data=json.dumps(self._build_payload(test_project, 'TRANSFER')),
            content_type='application/json',
        )

        assert response.status_code == 201
        payload = response.json()['data']
        guide = ShippingGuide.objects.get(pk=payload['id'])

        assert payload['origin_place'] == 'ORIGEN MANUAL'
        assert payload['destination_place'] == 'DESTINO MANUAL'
        assert guide.origin_place == 'ORIGEN MANUAL'
        assert guide.destination_place == 'DESTINO MANUAL'

    def test_report_uses_saved_places(self, client_logged, test_project):
        guide = ShippingGuide.objects.create(
            project=test_project,
            type_shipping_guide='EXIT',
            issue_date=date.today(),
            origin_place='BODEGA TEMPORAL',
            destination_place='DESTINO INCORRECTO',
            id_user_created=test_project.id_user_created,
            id_user_updated=test_project.id_user_updated,
        )

        response = client_logged.get(f'/reports/template-shipping-guide/{guide.id}/')
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'BODEGA TEMPORAL' in content
        assert 'DESTINO INCORRECTO' in content
