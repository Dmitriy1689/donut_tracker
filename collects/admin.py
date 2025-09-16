from django.contrib import admin

from collects.models import Collect


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'occasion', 'current_amount',
        'target_amount', 'end_datetime', 'created_at', 'is_completed'
    )
    list_filter = ('occasion', 'created_at', 'end_datetime')
    search_fields = ('title', 'author__username', 'description')
    readonly_fields = ('current_amount', 'donators_count', 'created_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('author', 'title', 'description', 'occasion')
        }),
        ('Финансовая информация', {
            'fields': ('target_amount', 'current_amount', 'donators_count')
        }),
        ('Даты и медиа', {
            'fields': ('end_datetime', 'cover_image', 'created_at')
        }),
    )

    @admin.display(description='Current Amount')
    def current_amount(self, obj):
        return obj.current_amount
