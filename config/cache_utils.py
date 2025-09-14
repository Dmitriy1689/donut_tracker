from django.core.cache import cache


def clear_collects_cache():
    """Очистка кэша для представлений Collect."""
    cache.delete_pattern('*collects*')


def clear_payments_cache():
    """Очистка кэша для представлений Payment."""
    cache.delete_pattern('*payments*')
