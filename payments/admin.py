from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'donator', 'collect', 'amount',
        'payment_datetime', 'hide_amount'
    )
    list_filter = ('payment_datetime', 'hide_amount')
    search_fields = ('donator__username', 'collect__title')
    readonly_fields = ('payment_datetime',)
    date_hierarchy = 'payment_datetime'
