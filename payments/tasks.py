import logging

from celery import shared_task

from payments.models import Payment


logger = logging.getLogger('payments_events')


@shared_task
def send_donation_email(payment_id):
    """Событие для логирования донатов."""
    try:
        payment = Payment.objects.get(id=payment_id)
        logger.info(
            f"Новый взнос: Donation #{payment.id}, "
            f"Сумма: {payment.amount}, "
            f"Сбор: {payment.collect.title}"
        )
    except Payment.DoesNotExist:
        logger.error(f"Взноса с id {payment_id} не существует!.")
