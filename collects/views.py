from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from collects.models import Collect
from collects.serializers import CollectSerializer
from payments.permissions import IsOwnerOrReadOnly


class CollectViewSet(viewsets.ModelViewSet):
    """Представление для модели Collect."""

    serializer_class = CollectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Collect.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
