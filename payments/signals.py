from django.db.models.signals import post_save
from django.dispatch import receiver

from payments.models import Payment
from payments.tasks import send_donation_email


@receiver(post_save, sender=Payment)
def handle_new_payment(sender, instance, created, **kwargs):
    """Обработчик сигнала для логирования новых взносов."""
    if created:
        send_donation_email.delay(instance.id)
