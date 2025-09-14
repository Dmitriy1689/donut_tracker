from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin
)
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.permissions import IsDonatorOrReadOnly
from payments.serializers import PaymentSerializer


class PaymentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    viewsets.GenericViewSet
):
    """Представление для модели Payment."""

    serializer_class = PaymentSerializer
    permission_classes = [IsDonatorOrReadOnly, IsAuthenticated]

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Payment.objects.none()

        collect_id = self.request.query_params.get('collect_id')
        queryset = Payment.objects.filter(donator=self.request.user)

        if collect_id:
            return queryset.filter(collect_id=collect_id)

        return queryset.order_by('-payment_datetime')

    def perform_create(self, serializer):
        serializer.save(donator=self.request.user)
