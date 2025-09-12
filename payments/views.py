from rest_framework import viewsets

from payments.models import Payment
from payments.permissions import IsOwnerOrReadOnly
from payments.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """Представление для модели Payment."""

    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Payment.objects.filter(
            donator=self.request.user
        ).order_by('-payment_datetime')

    def perform_create(self, serializer):
        serializer.save(donator=self.request.user)
