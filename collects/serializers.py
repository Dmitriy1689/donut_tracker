from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from payments.serializers import PaymentShortSerializer, UserShortSerializer
from collects.models import Collect


User = get_user_model()


class CollectSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Collect."""

    author_details = UserShortSerializer(source='author', read_only=True)
    payments = PaymentShortSerializer(many=True, read_only=True)
    current_amount = serializers.SerializerMethodField()
    donators_count = serializers.SerializerMethodField()

    class Meta:
        model = Collect
        fields = [
            'id',
            'author',
            'author_details',
            'title',
            'description',
            'occasion',
            'target_amount',
            'current_amount',
            'donators_count',
            'end_datetime',
            'created_at',
            'cover_image',
            'is_completed',
            'payments',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'author',
            'author_details',
            'is_completed',
        ]

    def validate_end_datetime(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                'Дата и время окончания сбора должны быть в будущем.'
            )
        return value

    def validate_target_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Целевая сумма должна быть положительным числом.'
            )
        return value

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def get_current_amount(self, obj):
        return getattr(obj, 'total_amount', 0) or obj.current_amount

    def get_donators_count(self, obj):
        return getattr(obj, 'total_donators', 0) or obj.donators_count
