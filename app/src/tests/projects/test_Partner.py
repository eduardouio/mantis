import pytest
from django.urls import reverse
from tests.BaseTestView import BaseTestView


class TestPartnerList(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('partner_list')

    def test_true(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert response.context['title_page'] == 'Listado de Socios de Negocio'
        object_list = response.context['object_list']
        assert len(object_list) > 0

