from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import serializers

from payments.models import Payment


User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления пользователя."""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']


class PaymentShortSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для модели Payment."""

    donator_username = serializers.CharField(
        source='donator.username', read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'donator_username', 'amount',
            'payment_datetime', 'hide_amount'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment."""

    donator_details = UserShortSerializer(source='donator', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'collect',
            'donator',
            'donator_details',
            'amount',
            'payment_datetime',
            'hide_amount',
        ]
        read_only_fields = [
            'id', 'payment_datetime', 'donator_details', 'donator'
        ]

    def validate(self, attrs):
        collect = attrs.get('collect')
        amount = attrs.get('amount')

        if collect.is_completed:
            raise serializers.ValidationError({
                'collect': 'Сбор уже завершен. Новые платежи не принимаются.'
            })

        if collect.target_amount is not None:
            current_total = (
                collect.payments.aggregate(total=Sum('amount'))['total'] or 0
            )
            remaining_amount = collect.target_amount - current_total

            if amount > remaining_amount:
                raise serializers.ValidationError({
                    'amount': (
                        f'Сумма платежа ({amount}) превышает оставшуюся сумму '
                        f'сбора. Максимально можно внести: {remaining_amount}'
                    )
                })
        return attrs

    def create(self, validated_data):
        validated_data['donator'] = self.context['request'].user
        return super().create(validated_data)
