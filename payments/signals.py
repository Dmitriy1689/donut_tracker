from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

import logging

from collects.models import Collect
from config.cache_utils import clear_collects_cache, clear_payments_cache
from payments.models import Payment


logger = logging.getLogger('payments')


@receiver(post_save, sender=Payment)
def update_collect_on_payment_create(sender, instance, created, **kwargs):
    if created:
        collect = instance.collect
        Collect.objects.filter(id=collect.id).update(
            current_amount=F('current_amount') + instance.amount,
            donators_count=F('donators_count') + 1
        )

        collect.refresh_from_db()

        logger.info(
            f'Новый взнос: {instance.donator.username} внес '
            f'{instance.amount} на счет сбора {collect.title}'
        )

        clear_collects_cache()
        clear_payments_cache()

        if (
            collect.target_amount is not None
            and collect.current_amount >= collect.target_amount
            and not collect.is_completed
        ):
            logger.info(
                f'Сбор "{collect.title}" достиг целевой суммы '
                f'{collect.target_amount} и закрыт для новых взносов.'
            )
            Collect.objects.filter(id=collect.id).update(is_completed=True)


@receiver(post_delete, sender=Payment)
def update_collect_on_payment_delete(sender, instance, **kwargs):
    collect = instance.collect
    Collect.objects.filter(id=collect.id).update(
        current_amount=F('current_amount') - instance.amount,
        donators_count=F('donators_count') - 1
    )

    collect.refresh_from_db()

    logger.info(
        f'Взнос отозван: {instance.donator.username} отозвал '
        f'{instance.amount} со счета сбора {collect.title}'
    )

    if (
        collect.target_amount is not None
        and collect.current_amount < collect.target_amount
        and collect.is_completed
    ):
        logger.info(
            f'Сбор "{collect.title}" снова открыт для новых взносов, '
            f'так как текущая сумма {collect.current_amount} '
            f'стала меньше целевой {collect.target_amount}.'
        )
        Collect.objects.filter(id=collect.id).update(is_completed=False)

    clear_collects_cache()
    clear_payments_cache()
