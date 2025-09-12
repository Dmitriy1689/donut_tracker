from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя, расширяющая стандартную модель AbstractUser.
    В данный момент не добавляет дополнительных полей, но может быть расширена
    в будущем для добавления специфичных атрибутов пользователя.
    """
    pass
