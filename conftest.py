import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для создания неаутентифицированного API клиента."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Фикстура для создания аутентифицированного API клиента."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user(db):
    """Фикстура для создания тестового пользователя."""
    return baker.make(User, username='testuser')


@pytest.fixture
def another_user(db):
    """Фикстура для создания еще одного тестового пользователя."""
    return baker.make(User, username='anotheruser')


@pytest.fixture
def collect(db, user):
    """Фикстура для создания тестового сбора средств."""
    return baker.make('collects.Collect', author=user, target_amount=10000)


@pytest.fixture
def completed_collect(db, user):
    """Фикстура для создания завершенного тестового сбора средств."""
    return baker.make(
        'collects.Collect',
        author=user,
        target_amount=1000,
        is_completed=True
    )


@pytest.fixture
def payment(db, collect, user):
    """Фикстура для создания тестового платежа."""
    return baker.make(
        'payments.Payment',
        collect=collect,
        donator=user,
        amount=1000
    )


@pytest.fixture
def payment_data(collect):
    """Фикстура для получения данных тестового платежа."""
    return {
        'collect': collect.id,
        'amount': 1500,
        'hide_amount': False
    }
