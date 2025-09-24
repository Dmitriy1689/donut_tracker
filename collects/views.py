from django.db.models import Count, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from collects.models import Collect
from collects.serializers import CollectSerializer
from collects.permissions import IsAuthorOrReadOnly


class CollectViewSet(viewsets.ModelViewSet):
    """Представление для модели Collect."""

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    serializer_class = CollectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Collect.objects.annotate(
            current_amount=Sum('payments__amount'),
            donators_count=Count('payments__donator', distinct=True)
        ).prefetch_related('payments__donator')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
