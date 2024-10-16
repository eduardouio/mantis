import pytest
from django.test import Client
from django.urls import reverse
from accounts.models import CustomUserModel

@pytest.mark.django_db
class BaseTestView():

    @pytest.fixture
    def client_logged(self):
        user = CustomUserModel.get(email='eduardouio7@gmail.com')
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture
    def client_not_logged(self):
        return Client()

    def test_client_logged(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200

    def test_client_not_logged(self, client_not_logged, url):
        response = client_not_logged.get(url)
        url_reponse = reverse('login') + '?next=' + url
        assert response.status_code == 302
        assert response.url == url_reponse
