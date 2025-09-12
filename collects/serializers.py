from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from payments.serializers import UserShortSerializer
from collects.models import Collect


User = get_user_model()


class CollectSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Collect."""

    author_details = UserShortSerializer(source='author', read_only=True)

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
        ]
        read_only_fields = [
            'id',
            'created_at',
            'author_details',
            'current_amount',
            'donators_count',
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
