from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from model_bakery import baker
from rest_framework import status

from collects.models import Collect
from collects.serializers import CollectSerializer
from payments.serializers import PaymentSerializer


def test_payment_creation(
        collect,
        user,
        authenticated_client,
        payment_data
):
    """Тест на корректное создание платежа через ORM."""
    payment = baker.make(
        'payments.Payment',
        collect=collect,
        donator=user,
        amount=500
    )
    response = authenticated_client.post('/api/v1/payments/', payment_data)

    assert Decimal(response.data['amount']) == Decimal(payment_data['amount'])
    assert response.data['collect'] == payment_data['collect']
    assert 'id' in response.data
    assert payment.collect == collect
    assert payment.donator == user
    assert payment.amount == 500
    assert not payment.hide_amount


def test_collect_current_amount(
        collect,
        user,
        authenticated_client,
        payment_data
):
    """Тест на корректную калькуляцию платежей."""
    baker.make(
        'payments.Payment',
        collect=collect,
        donator=user,
        amount=1000,
        _quantity=3
    )

    collect = (
        Collect.objects
        .annotate(
            total_amount=Sum("payments__amount"),
            total_donators=Count("payments__donator", distinct=True)
        )
        .get(id=collect.id)
    )

    response = authenticated_client.post('/api/v1/payments/', payment_data)
    assert Decimal(response.data['amount']) == Decimal(payment_data['amount'])
    assert response.data['collect'] == payment_data['collect']
    assert 'id' in response.data
    assert collect.total_amount == 3000
    assert collect.total_donators == 1


def test_collect_multiple_donators(collect, user, another_user):
    """Тест на корректную калькуляцию донатеров."""
    baker.make(
        'payments.Payment',
        collect=collect, donator=user,
        amount=1000
    )
    baker.make(
        'payments.Payment',
        collect=collect,
        donator=another_user,
        amount=2000
    )

    collect = (
        Collect.objects
        .annotate(
            total_amount=Sum("payments__amount"),
            total_donators=Count("payments__donator", distinct=True)
        )
        .get(id=collect.id)
    )

    assert collect.total_amount == 3000
    assert collect.total_donators == 2


def test_create_collect(authenticated_client, user):
    """Тест на корректное создание сбора."""
    data = {
        'title': 'Medical Treatment',
        'description': 'Fundraising for medical expenses',
        'occasion': 'medicine',
        'target_amount': 50000,
        'end_datetime': '2028-12-31T23:59:59Z'
    }

    response = authenticated_client.post('/api/v1/collects/', data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['author'] == user.id
    assert response.data['title'] == data['title']


def test_create_payment(authenticated_client, collect, payment_data):
    """Тест на корректное создание платежа через API."""
    response = authenticated_client.post('/api/v1/payments/', payment_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Decimal(response.data['amount']) == Decimal(payment_data['amount'])
    assert response.data['collect'] == collect.id


def test_list_only_own_payments(authenticated_client, user, another_user):
    """Пользователь получает список только своих платежей."""
    collect = baker.make('collects.Collect', author=another_user)

    baker.make(
        'payments.Payment',
        collect=collect,
        donator=user,
        amount=1000
    )
    baker.make(
        'payments.Payment',
        collect=collect,
        donator=another_user,
        amount=2000
    )

    response = authenticated_client.get('/api/v1/payments/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['amount'] == '1000.00'


def test_filter_payments_by_collect(authenticated_client, user):
    """Проверка правильности работы фильтра collect_id."""
    collect1 = baker.make('collects.Collect', author=user)
    collect2 = baker.make('collects.Collect', author=user)

    baker.make('payments.Payment', collect=collect1, donator=user, amount=1000)
    baker.make('payments.Payment', collect=collect2, donator=user, amount=2000)

    response = authenticated_client.get(
        f'/api/v1/payments/?collect_id={collect1.id}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['amount'] == '1000.00'


def test_unauthenticated_access(api_client):
    """Проверка ограничения прав доступа к списку платежей."""
    response = api_client.get('/api/v1/payments/')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_collect_serializer_end_date_validation(user):
    """Тест валидации даты окончания сбора."""
    data = {
        'title': 'Test Collect',
        'description': 'Test Description',
        'occasion': 'birthday',
        'target_amount': 10000,
        'end_datetime': timezone.now() - timezone.timedelta(days=1)
    }

    serializer = CollectSerializer(data=data, context={'request': None})
    assert not serializer.is_valid()
    assert 'end_datetime' in serializer.errors


def test_payment_serializer_amount_validation(collect, user):
    """Тест валидации превышенной суммы платежа."""
    data = {
        'collect': collect.id,
        'amount': collect.target_amount + 1000,
        'hide_amount': False
    }

    serializer = PaymentSerializer(data=data, context={'request': None})
    assert not serializer.is_valid()
    assert 'amount' in serializer.errors


def test_payment_hide_amount(authenticated_client, collect, user):
    """Проверка, что скрытие суммы платежа работает."""
    data = {'collect': collect.id, 'amount': 1000, 'hide_amount': True}
    response = authenticated_client.post('/api/v1/payments/', data)

    assert response.status_code == 201
    assert response.data['hide_amount'] is True


def test_collect_serializer_minimal_data(user):
    """Проверка, что сериализатор Collect валиден с минимальными данными."""
    data = {
        'title': 'Test',
        'description': 'Desc',
        'occasion': 'other',
        'end_datetime': timezone.now() + timedelta(days=1),
    }
    serializer = CollectSerializer(data=data, context={'request': None})
    assert serializer.is_valid()


def test_create_payment_on_completed_collect(
    authenticated_client, completed_collect
):
    """Проверка, что нельзя внести платеж в завершенный сбор."""
    data = {
        'collect': completed_collect.id,
        'amount': 500,
        'hide_amount': False
    }
    response = authenticated_client.post('/api/v1/payments/', data)

    assert response.status_code == 400
