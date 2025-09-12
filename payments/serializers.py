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
        read_only_fields = ['id', 'payment_datetime', 'donator_details']

    def create(self, validated_data):
        validated_data['donator'] = self.context['request'].user
        return super().create(validated_data)
