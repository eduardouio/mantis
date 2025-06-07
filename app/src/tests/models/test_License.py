# Archivo de pruebas para el modelo License
# ...aquí van los tests para License...

import pytest
from datetime import date, timedelta
from accounts.models.License import License
from accounts.models.CustomUserModel import CustomUserModel


@pytest.mark.django_db
class TestLicense:
    
    def test_create_license(self):
        user = CustomUserModel.objects.create_user(
            email='test@example.com',
            password='pass123'
        )
        license = License.objects.create(
            license_key='TEST-LICENSE-123',
            role='ADMINISTRATIVO',
            enterprise='PEISOL S.A.',
            user=user
        )
        assert license.license_key == 'TEST-LICENSE-123'
        assert license.role == 'ADMINISTRATIVO'
        assert license.enterprise == 'PEISOL S.A.'
        assert not license.is_active  # default False
        assert license.user == user

    def test_license_activation(self):
        user = CustomUserModel.objects.create_user(
            email='test@example.com',
            password='pass123'
        )
        license = License.objects.create(
            license_key='ACTIVE-LICENSE-456',
            activated_on=date.today(),
            expires_on=date.today() + timedelta(days=365),
            is_active=True,
            user=user
        )
        assert license.is_active
        assert license.activated_on == date.today()
        assert license.expires_on == date.today() + timedelta(days=365)

    def test_license_unique_key(self):
        user1 = CustomUserModel.objects.create_user(
            email='user1@example.com',
            password='pass123'
        )
        user2 = CustomUserModel.objects.create_user(
            email='user2@example.com',
            password='pass123'
        )
        
        License.objects.create(
            license_key='UNIQUE-KEY-789',
            user=user1
        )
        
        # Should raise IntegrityError for duplicate license_key
        with pytest.raises(Exception):
            License.objects.create(
                license_key='UNIQUE-KEY-789',
                user=user2
            )
