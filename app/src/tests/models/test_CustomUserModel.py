import pytest
from django.contrib.auth import get_user_model
from accounts.models.CustomUserModel import CustomUserModel

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        assert user.email == 'test@example.com'
        assert user.role == 'TECNICO'  # default role
        assert not user.is_confirmed_mail  # default False
        assert user.check_password('testpass123')
        assert str(user) == 'test@example.com'

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin.email == 'admin@example.com'
        assert admin.is_staff
        assert admin.is_superuser

    def test_user_get_method(self):
        User.objects.create_user(
            email='existing@example.com',
            password='pass123'
        )
        
        # Test existing user
        user = CustomUserModel.get('existing@example.com')
        assert user is not None
        assert user.email == 'existing@example.com'
        
        # Test non-existing user
        user = CustomUserModel.get('nonexistent@example.com')
        assert user is None

    def test_user_role_choices(self):
        admin_user = User.objects.create_user(
            email='admin@example.com',
            password='pass123',
            role='ADMINISTRATIVO'
        )
        assert admin_user.role == 'ADMINISTRATIVO'

    def test_email_as_username(self):
        user = User.objects.create_user(
            email='username@example.com',
            password='pass123'
        )
        assert user.username is None
        assert user.USERNAME_FIELD == 'email'
