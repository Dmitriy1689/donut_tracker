from django.contrib.auth import get_user_model
from django.db import models

from collects.constants import AMOUNT_DECIMAL_PLACES, AMOUNT_MAX_DIGITS
from collects.models import Collect

User = get_user_model()


class Payment(models.Model):
    """
    Модель для хранения информации о платежах, связанных с денежными сборами.
    Каждый платеж связан с конкретным сбором и пользователем,
    который его совершил.
    """

    collect = models.ForeignKey(
        Collect,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Сбор',
    )
    donator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Донатер',
    )
    amount = models.DecimalField(
        max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        verbose_name='Сумма платежа',
    )
    payment_datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время платежа',
    )
    hide_amount = models.BooleanField(
        default=False,
        verbose_name='Скрыть сумму в ленте',
    )

    def __str__(self):
        return (
            f'Платеж на сумму {self.amount} от {self.donator} '
            f'для сбора {self.collect.title}'
        )

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_datetime']
