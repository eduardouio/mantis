import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from accounts.models import Technical
from accounts.models.VaccinationRecord import VaccinationRecord


@pytest.mark.django_db
class TestCreateUpdateVaccineAPI:
    """Tests para CreateUpdateVaccineAPI"""

    @pytest.fixture
    def client_logged(self):
        user, _ = CustomUserModel.objects.get_or_create(
            email="test@example.com",
            defaults={
                "first_name": "Test",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture
    def technical(self):
        return Technical.objects.create(
            first_name="Jane",
            last_name="Smith",
            dni="0987654321",
            nro_phone="0888888888",
        )

    @pytest.fixture
    def valid_data(self, technical):
        return {
            "technical_id": technical.id,
            "vaccine_type": "COVID",
            "application_date": date.today().strftime("%Y-%m-%d"),
            "dose_number": 1,
        }

    def endpoint(self):
        return "/api/technicals/create_update_vaccine/"

    def test_create_success(self, client_logged, valid_data):
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(valid_data),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["success"] is True
        assert data["data"]["vaccine_type"] == "COVID"
        assert VaccinationRecord.objects.filter(
            id=data["data"]["id"], is_active=True
        ).exists()

    def test_create_missing_fields(self, client_logged):
        payload = {"vaccine_type": "COVID"}
        resp = client_logged.post(
            self.endpoint(), data=json.dumps(payload), content_type="application/json"
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert data["success"] is False
        assert "Campo" in data["error"]

    def test_create_invalid_technical(self, client_logged, valid_data):
        valid_data["technical_id"] = 999999
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(valid_data),
            content_type="application/json",
        )
        assert resp.status_code == 500

    def test_create_invalid_date_format(self, client_logged, valid_data):
        valid_data["application_date"] = "2024-13-45"
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(valid_data),
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert "application_date formato" in data["error"]

    def test_create_invalid_next_dose_date(self, client_logged, valid_data):
        valid_data["next_dose_date"] = "2024-14-40"
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(valid_data),
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert "next_dose_date formato" in data["error"]

    def test_create_invalid_type(self, client_logged, valid_data):
        valid_data["vaccine_type"] = "INVALID"
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(valid_data),
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert "Tipo vacuna invalido" in data["error"]

    def test_update_success(self, client_logged, technical):
        record = VaccinationRecord.objects.create(
            technical=technical, vaccine_type="COVID", application_date=date.today()
        )
        payload = {
            "id": record.id,
            "technical_id": technical.id,
            "vaccine_type": "TETANUS",
            "application_date": date.today().strftime("%Y-%m-%d"),
            "dose_number": 2,
        }
        resp = client_logged.put(
            self.endpoint(), data=json.dumps(payload), content_type="application/json"
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["success"] is True
        assert data["data"]["vaccine_type"] == "TETANUS"
        record.refresh_from_db()
        assert record.vaccine_type == "TETANUS"

    def test_update_missing_id(self, client_logged, valid_data):
        resp = client_logged.put(
            self.endpoint(),
            data=json.dumps(valid_data),
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert "ID requerido" in data["error"]

    def test_get_by_id(self, client_logged, technical):
        record = VaccinationRecord.objects.create(
            technical=technical, vaccine_type="COVID", application_date=date.today()
        )
        url = f"{self.endpoint()}?id={record.id}"
        resp = client_logged.get(url)
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["success"] is True
        assert data["data"]["id"] == record.id

    def test_get_by_technical(self, client_logged, technical):
        VaccinationRecord.objects.create(
            technical=technical, vaccine_type="COVID", application_date=date.today()
        )
        VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type="TETANUS",
            application_date=date.today() - timedelta(days=10),
        )
        url = f"{self.endpoint()}?technical_id={technical.id}"
        resp = client_logged.get(url)
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["success"] is True
        assert len(data["data"]) == 2

    def test_get_all(self, client_logged, technical):
        VaccinationRecord.objects.create(
            technical=technical, vaccine_type="COVID", application_date=date.today()
        )
        resp = client_logged.get(self.endpoint())
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["success"] is True
        assert len(data["data"]) >= 1

    def test_invalid_json(self, client_logged):
        resp = client_logged.post(
            self.endpoint(), data="invalid json", content_type="application/json"
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert "JSON invalido" in data["error"]
