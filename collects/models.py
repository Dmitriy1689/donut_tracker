from django.db import models
from django.contrib.auth import get_user_model

from collects.constants import (
    AMOUNT_DECIMAL_PLACES,
    AMOUNT_DEFAULT_VALUE,
    AMOUNT_MAX_DIGITS,
    DESCRIPTION_LENGTH_LIMIT,
    DONATORS_DEFAULT_VALUE,
    TITLE_LENGTH_LIMIT,
)


User = get_user_model()


class Collect(models.Model):
    """
    Модель для хранения информации о финансовых сборах.
    Каждая операция связана с пользователем и содержит информацию о сумме,
    дате, категории и описании операции.
    """

    class Occasion(models.TextChoices):
        """Возможные поводы для сбора средств."""

        BIRTHDAY = 'birthday', 'День рождения'
        WEDDING = 'wedding', 'Свадьба'
        CHARITY = 'charity', 'Благотворительность'
        MEDICINE = 'medicine', 'Медицина'
        EDUCATION = 'education', 'Образование'
        OTHER = 'other', 'Другое'

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='collects',
        verbose_name='Автор сбора',
    )
    title = models.CharField(
        max_length=TITLE_LENGTH_LIMIT,
        verbose_name='Название сбора',
    )
    description = models.TextField(
        max_length=DESCRIPTION_LENGTH_LIMIT,
        verbose_name='Описание',
    )
    occasion = models.CharField(
        max_length=20,
        verbose_name='Повод',
        choices=Occasion.choices,
    )
    target_amount = models.DecimalField(
        max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        verbose_name='Целевая сумма',
        null=True,
        blank=True,
    )
    current_amount = models.DecimalField(
        max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        verbose_name='Собранная сумма',
        default=AMOUNT_DEFAULT_VALUE,
    )
    donators_count = models.PositiveIntegerField(
        verbose_name='Количество донатеров',
        default=DONATORS_DEFAULT_VALUE,
    )
    end_datetime = models.DateTimeField(
        verbose_name='Дата и время окончания сбора',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    cover_image = models.ImageField(
        upload_to='collect_covers/',
        null=True,
        blank=True,
        verbose_name='Обложка сбора',
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Сбор завершен',
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = 'Денежный сбор'
        verbose_name_plural = 'Денежные сборы'
        ordering = ['-created_at']
