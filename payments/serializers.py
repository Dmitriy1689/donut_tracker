from django.contrib.auth import get_user_model
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
        """Проверяем, что платеж не превышает оставшуюся сумму сбора."""
        collect = attrs.get('collect')
        amount = attrs.get('amount')

        if collect.target_amount is not None:
            current_total = collect.current_amount
            remaining_amount = collect.target_amount - current_total

            if amount > remaining_amount:
                raise serializers.ValidationError(
                    f'Сумма платежа ({amount}) превышает оставшуюся сумму '
                    f'сбора. Максимально можно внести: {remaining_amount} '
                )
        return attrs

    def create(self, validated_data):
        validated_data['donator'] = self.context['request'].user
        return super().create(validated_data)
