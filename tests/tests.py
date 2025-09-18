from decimal import Decimal
from model_bakery import baker
from rest_framework import status


def test_payment_creation(collect, user):
    """Тест на корректное создание платежа через ORM."""
    payment = baker.make(
        'payments.Payment',
        collect=collect,
        donator=user,
        amount=500
    )

    assert payment.collect == collect
    assert payment.donator == user
    assert payment.amount == 500
    assert not payment.hide_amount


def test_collect_current_amount(collect, user):
    """Тест на корректную калькуляцию платежей."""
    baker.make(
        'payments.Payment',
        collect=collect,
        donator=user,
        amount=1000,
        _quantity=3
    )

    assert collect.current_amount == 3000
    assert collect.donators_count == 1


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

    assert collect.current_amount == 3000
    assert collect.donators_count == 2


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
